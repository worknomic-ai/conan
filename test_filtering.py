import json
import os
import re

from conan.tools.env import VirtualBuildEnv
from conans.test.utils.tools import TestClient

def test_graph_info_filtering():
    client = TestClient()
    client.save({
        "dep/conanfile.py": """
from conan import ConanFile
class Dep(ConanFile):
    name = "dep"
""",
        "pkg_a/conanfile.py": """
from conan import ConanFile
class PkgA(ConanFile):
    name = "pkga"
    version = "1.0"
    def requirements(self):
        self.requires("dep/1.0")
""",
        "pkg_b/conanfile.py": """
from conan import ConanFile
class PkgB(ConanFile):
    name = "pkgb"
    version = "1.0"
    def requirements(self):
        self.requires("dep/2.0")
""",
        "conanfile.py": """
from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    def requirements(self):
        self.requires("pkga/1.0")
        self.requires("pkgb/1.0")
"""
    })
    client.run("create dep/conanfile.py --version 1.0")
    client.run("create dep/conanfile.py --version 2.0")
    client.run("create pkg_a/conanfile.py")
    client.run("create pkg_b/conanfile.py")
    
    try:
        client.run("graph info conanfile.py --format=html", assert_error=True)
    except Exception as e:
        print("Exception", e)
    
    html = str(client.out)
    print("HTML out:")
    print("HTML out length:", len(html))
    import re
    m1 = re.search(r"var nodes = \[([\s\S]*?)\]\n            var edges = \[", html)
    if m1:
        print("Nodes array:", m1.group(1))

    m2 = re.search(r"// Add error conflict node([\s\S]*?)\]\)", html)
    if m2:
        print("Conflict section:", m2.group(1))




test_graph_info_filtering()
