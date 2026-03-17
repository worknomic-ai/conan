import pytest
from conans.test.utils.tools import TestClient, GenConanfile
import json
import textwrap

def test_dynamic_host_version():
    c = TestClient()
    pkg = textwrap.dedent("""
        from conan import ConanFile
        class MyTool(ConanFile):
            name = "mytool"
            def requirements(self):
                self.requires("pkg/1.0")
            def build_requirements(self):
                self.tool_requires("mytool/<host_version:pkg>")
        """)
    c.save({"pkg/conanfile.py": GenConanfile("pkg"),
            "mytool/conanfile.py": pkg})
    c.run("create pkg --version=1.0")
    c.run("create mytool --version=1.0", assert_error=True) 
    # wait, if mytool needs mytool/1.0 as a tool_require, we need to build mytool/1.0 first, but it circularly requires itself?
    # No, we can just tool_require "other/1.0". Let's use "other".
    
    pkg2 = textwrap.dedent("""
        from conan import ConanFile
        class MyTool(ConanFile):
            name = "mytool"
            def requirements(self):
                self.requires("pkg/1.0")
            def build_requirements(self):
                self.tool_requires("other/<host_version:pkg>")
        """)
    c.save({"mytool/conanfile.py": pkg2, "other/conanfile.py": GenConanfile("other")})
    c.run("create other --version=1.0")
    c.run("create mytool --version=1.0")
    
    c.run("graph info mytool --version=1.0 --format=json")
    out = json.loads(c.stdout)
    nodes = out["graph"]["nodes"]
    for id, node in nodes.items():
        if "mytool" in node.get("ref", ""):
            for dep in node.get("dependencies", {}).values():
                print("MYTOOL DEP:", dep["ref"])
                
test_dynamic_host_version()
