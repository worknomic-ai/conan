import pytest
from conans.test.utils.tools import TestClient

def test_dependencies_in():
    client = TestClient()
    client.save({
        "dep/conanfile.py": """from conan import ConanFile
class Dep(ConanFile):
    name = "dep"
    version = "1.0"
""",
        "pkg/conanfile.py": """from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    requires = "dep/1.0"

    def generate(self):
        if "dep" in self.dependencies:
            self.output.info("dep is in dependencies!")
        if "missing_pkg" not in self.dependencies:
            self.output.info("missing_pkg is NOT in dependencies!")
"""
    })
    client.run("create dep")
    client.run("create pkg")
    assert "dep is in dependencies!" in client.out
    assert "missing_pkg is NOT in dependencies!" in client.out


def test_dependencies_in_build():
    client = TestClient()
    client.save({
        "dep/conanfile.py": """from conan import ConanFile
class Dep(ConanFile):
    name = "dep"
    version = "1.0"
""",
        "pkg/conanfile.py": """from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    tool_requires = "dep/1.0"

    def generate(self):
        if "dep" in self.dependencies.build:
            self.output.info("dep is in dependencies.build!")
        if "dep" not in self.dependencies:
            self.output.info("dep is NOT in dependencies(host)!")
"""
    })
    client.run("create dep")
    client.run("create pkg")
    assert "dep is in dependencies.build!" in client.out
    assert "dep is NOT in dependencies(host)!" in client.out

def test_dependencies_in_invalid_ref():
    client = TestClient()
    client.save({
        "pkg/conanfile.py": """from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"

    def generate(self):
        if "invalid ref/" in self.dependencies:
            self.output.error("invalid ref should not be in dependencies!")
        else:
            self.output.info("invalid ref is NOT in dependencies!")
"""
    })
    client.run("create pkg")
    assert "invalid ref is NOT in dependencies!" in client.out

def test_dependencies_in_req_object():
    client = TestClient()
    client.save({
        "dep/conanfile.py": """from conan import ConanFile
class Dep(ConanFile):
    name = "dep"
    version = "1.0"
""",
        "pkg/conanfile.py": """from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    requires = "dep/1.0"

    def generate(self):
        req = [r for r, _ in self.dependencies.items()][0]
        if req in self.dependencies:
            self.output.info("req object is in dependencies!")
"""
    })
    client.run("create dep")
    client.run("create pkg")
    assert "req object is in dependencies!" in client.out
