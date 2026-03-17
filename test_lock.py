import pytest
from conans.test.utils.tools import TestClient, GenConanfile
import json
import textwrap

def test_dynamic_host_version_lockfile():
    c = TestClient()
    pkg2 = textwrap.dedent("""
        from conan import ConanFile
        class MyTool(ConanFile):
            name = "mytool"
            def requirements(self):
                self.requires("pkg/1.0")
            def build_requirements(self):
                self.tool_requires("other/<host_version:pkg>")
        """)
    c.save({
        "pkg/conanfile.py": GenConanfile("pkg"),
        "other/conanfile.py": GenConanfile("other"),
        "mytool/conanfile.py": pkg2
    })
    c.run("create pkg --version=1.0")
    c.run("create other --version=1.0")
    c.run("lock create mytool/conanfile.py --version=1.0")
    
    with open(c.current_folder + "/mytool/conan.lock") as f:
        lock = json.load(f)
        
    print(json.dumps(lock, indent=2))

test_dynamic_host_version_lockfile()
