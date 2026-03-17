import pytest

from conans.test.utils.tools import TestClient, GenConanfile

def test_info_clear_removes_tool_and_python_requires():
    client = TestClient()
    client.save({
        "tool/conanfile.py": GenConanfile("tool", "1.0"),
        "pyreq/conanfile.py": GenConanfile("pyreq", "1.0"),
        "header/conanfile.py": """
from conan import ConanFile

class Pkg(ConanFile):
    name = "header"
    version = "1.0"
    python_requires = "pyreq/1.0"
    tool_requires = "tool/1.0"

    def package_id(self):
        self.info.clear()
"""
    })
    client.run("create tool")
    client.run("create pyreq")
    client.run("create header")
    
    assert "header/1.0: Created package" in client.out
    out1 = str(client.out)
    
    # Get the package ID
    import re
    match = re.search(r"header/1.0: Package '([a-f0-9]+)' created", out1)
    assert match is not None
    pkg_id1 = match.group(1)
    
    # Now modify the versions
    client.save({
        "tool/conanfile.py": GenConanfile("tool", "2.0"),
        "pyreq/conanfile.py": GenConanfile("pyreq", "2.0"),
        "header/conanfile.py": """
from conan import ConanFile

class Pkg(ConanFile):
    name = "header"
    version = "1.0"
    python_requires = "pyreq/2.0"
    tool_requires = "tool/2.0"

    def package_id(self):
        self.info.clear()
"""
    })
    client.run("create tool")
    client.run("create pyreq")
    client.run("create header")
    
    out2 = str(client.out)
    match = re.search(r"header/1.0: Package '([a-f0-9]+)' created", out2)
    assert match is not None
    pkg_id2 = match.group(1)
    
    assert pkg_id1 == pkg_id2

