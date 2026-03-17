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
    
    client.run("graph explain conanfile.py")
    
    # Assert output is printed to stdout
    assert "Conflict detected:" in client.stdout
    assert "pkg/1.0 -> dep/1.0 -> conflict/1.0" in client.stdout
    assert "pkg/1.0 -> dep2/1.0 -> conflict/2.0" in client.stdout
    assert "Conflict detected:" not in client.stderr

def test_graph_explain_missing_binary():
    client = TestClient()
    client.save({
        "conanfile.py": """
from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    settings = "os"
""",
        "consumer.py": """
from conan import ConanFile
class Consumer(ConanFile):
    name = "consumer"
    version = "1.0"
    settings = "os"
    def requirements(self):
        self.requires("pkg/1.0")
"""
    })
    
    client.run("create conanfile.py -s os=Linux")
    
    # Require it with different os
    client.run("graph explain consumer.py -s os=Windows")
    
    # Verify the output in stdout
    assert "Graph explanation: Missing binaries found" in client.stdout
    assert "Missing binary for: pkg/1.0" in client.stdout
    assert "Requested os=Windows, but available are: Linux" in client.stdout
    
    # Verify not in stderr
    assert "Graph explanation:" not in client.stderr


def test_graph_explain_conflict_ranges():
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
        self.requires("conflict/[>=1.0 <2.0]")
""",
        "dep2/conanfile.py": """
from conan import ConanFile
class Dep2(ConanFile):
    name = "dep2"
    version = "1.0"
    def requirements(self):
        self.requires("conflict/[>=2.0 <3.0]")
""",
        "conflict1/conanfile.py": """
from conan import ConanFile
class Conflict(ConanFile):
    name = "conflict"
    version = "1.5"
""",
        "conflict2/conanfile.py": """
from conan import ConanFile
class Conflict(ConanFile):
    name = "conflict"
    version = "2.5"
"""
    })
    
    client.run("create conflict1/conanfile.py")
    client.run("create conflict2/conanfile.py")
    client.run("create dep/conanfile.py")
    client.run("create dep2/conanfile.py")
    
    client.run("graph explain conanfile.py")
    
    # We should see the conflict with the range text unescaped (since rich formatting shouldn't eat it)
    assert "Conflict detected:" in client.stdout
    assert "pkg/1.0 -> dep/1.0 -> conflict/1.5" in client.stdout
    assert "pkg/1.0 -> dep2/1.0 -> conflict/[>=2.0 <3.0]" in client.stdout
    
    assert "Conflict detected:" not in client.stderr


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
    assert "Conflict detected:" in client.stdout
    assert "conanfile.txt -> dep/1.0 -> conflict/1.0" in client.stdout
    assert "conanfile.txt -> dep2/1.0 -> conflict/2.0" in client.stdout
    assert "Conflict detected:" not in client.stderr
