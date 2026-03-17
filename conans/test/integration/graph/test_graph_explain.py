import pytest
from conans.test.utils.tools import TestClient

def test_graph_explain_conflict():
    client = TestClient()
    client.save({
        "conanfile.py": """
from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    def requirements(self):
        self.requires("dep/1.0")
        self.requires("dep2/1.0")
""",
        "dep/conanfile.py": """
from conan import ConanFile
class Dep(ConanFile):
    name = "dep"
    version = "1.0"
    def requirements(self):
        self.requires("conflict/1.0")
""",
        "dep2/conanfile.py": """
from conan import ConanFile
class Dep2(ConanFile):
    name = "dep2"
    version = "1.0"
    def requirements(self):
        self.requires("conflict/2.0")
""",
        "conflict1/conanfile.py": """
from conan import ConanFile
class Conflict(ConanFile):
    name = "conflict"
    version = "1.0"
""",
        "conflict2/conanfile.py": """
from conan import ConanFile
class Conflict(ConanFile):
    name = "conflict"
    version = "2.0"
"""
    })
    
    client.run("create conflict1/conanfile.py")
    client.run("create conflict2/conanfile.py")
    client.run("create dep/conanfile.py")
    client.run("create dep2/conanfile.py")
    
    client.run("graph explain .")
    out = client.out
    print(out)
    assert "Conflict detected:" in out
    assert "pkg/1.0 -> dep/1.0 -> conflict/1.0" in out
    assert "pkg/1.0 -> dep2/1.0 -> conflict/2.0" in out

def test_graph_explain_conflict_txt():
    client = TestClient()
    client.save({
        "conanfile.txt": """
[requires]
dep/1.0
dep2/1.0
""",
        "dep/conanfile.py": """
from conan import ConanFile
class Dep(ConanFile):
    name = "dep"
    version = "1.0"
    def requirements(self):
        self.requires("conflict/1.0")
""",
        "dep2/conanfile.py": """
from conan import ConanFile
class Dep2(ConanFile):
    name = "dep2"
    version = "1.0"
    def requirements(self):
        self.requires("conflict/2.0")
""",
        "conflict1/conanfile.py": """
from conan import ConanFile
class Conflict(ConanFile):
    name = "conflict"
    version = "1.0"
""",
        "conflict2/conanfile.py": """
from conan import ConanFile
class Conflict(ConanFile):
    name = "conflict"
    version = "2.0"
"""
    })
    
    client.run("create conflict1/conanfile.py")
    client.run("create conflict2/conanfile.py")
    client.run("create dep/conanfile.py")
    client.run("create dep2/conanfile.py")
    
    client.run("graph explain conanfile.txt")
    out = client.out
    print(out)
    assert "Conflict detected:" in out
    assert "conanfile.txt -> dep/1.0 -> conflict/1.0" in out
    assert "conanfile.txt -> dep2/1.0 -> conflict/2.0" in out
