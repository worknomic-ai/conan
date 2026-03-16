import pytest
from conans.test.utils.tools import TestClient, GenConanfile

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
