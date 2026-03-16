import pytest

from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

def test_header_only_clear():
    client = TestClient()
    client.save({
        "conanfile_b.py": GenConanfile("pkgb", "1.0"),
        "conanfile_a.py": """
from conan import ConanFile
class PkgA(ConanFile):
    name = "pkga"
    version = "1.0"
    requires = "pkgb/1.0"
    def package_id(self):
        self.info.clear()
""",
        "conanfile_c.py": GenConanfile("pkgc", "1.0").with_require("pkga/1.0"),
    })
    
    client.run("create conanfile_b.py")
    client.run("create conanfile_a.py")
    client.run("create conanfile_c.py")

    # verify pkga is correctly flagged as header-only
    client.run("graph info conanfile_a.py")
    assert "package_type: header-library" in client.out

def test_header_only_clear_removes_python_and_tool_requires():
    client = TestClient()
    
    # Create a python require
    client.save({
        "pyreq/conanfile.py": GenConanfile("pyreq", "1.0").with_package_type("python-require")
    })
    client.run("create pyreq")
    
    # Create a tool require
    client.save({
        "tool/conanfile.py": GenConanfile("tool", "1.0")
    })
    client.run("create tool")

    # Create a header-only package that uses self.info.clear()
    client.save({
        "header/conanfile.py": """
from conan import ConanFile

class HeaderOnly(ConanFile):
    name = "header"
    version = "1.0"
    python_requires = "pyreq/1.0"
    tool_requires = "tool/1.0"
    
    def package_id(self):
        self.info.clear()
"""
    })
    client.run("create header")
    output = client.out
    
    # Extract the package ID
    import re
    match = re.search(r"header/1.0: Package '([a-f0-9]+)' created", output)
    assert match is not None
    pkg_id_1 = match.group(1)
    
    # Now update the python_requires and tool_requires to 2.0
    client.save({
        "pyreq/conanfile.py": GenConanfile("pyreq", "2.0").with_package_type("python-require"),
        "tool/conanfile.py": GenConanfile("tool", "2.0")
    })
    client.run("create pyreq")
    client.run("create tool")
    
    # Create the header-only package again with the updated versions
    client.save({
        "header/conanfile.py": """
from conan import ConanFile

class HeaderOnly(ConanFile):
    name = "header"
    version = "1.0"
    python_requires = "pyreq/2.0"
    tool_requires = "tool/2.0"
    
    def package_id(self):
        self.info.clear()
"""
    })
    client.run("create header")
    output = client.out
    
    match = re.search(r"header/1.0: Package '([a-f0-9]+)' created", output)
    assert match is not None
    pkg_id_2 = match.group(1)
    
    # They should be the same
    assert pkg_id_1 == pkg_id_2

