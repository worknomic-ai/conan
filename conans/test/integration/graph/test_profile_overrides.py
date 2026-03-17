import pytest

from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

def test_replace_requires_direct():
    client = TestClient()
    client.save({
        "mydep/conanfile.py": GenConanfile("mydep", "1.0"),
        "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_require("dep/1.0"),
        "profile": "[replace_requires]\ndep/*: mydep/1.0"
    })
    client.run("create mydep")
    client.run("create pkg -pr profile")
    assert "mydep/1.0" in client.out
    assert "dep/1.0 - Cache" not in client.out
    assert "dep/1.0 - Build" not in client.out
    assert "dep/1.0 - Missing" not in client.out

def test_replace_requires_transitive():
    client = TestClient()
    client.save({
        "mydep/conanfile.py": GenConanfile("mydep", "1.0"),
        "dep/conanfile.py": GenConanfile("dep", "1.0").with_require("transitive/1.0"),
        "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_require("dep/1.0"),
        "profile": "[replace_requires]\ntransitive/*: mydep/1.0"
    })
    client.run("create mydep")
    client.run("export dep")
    client.run("create pkg -pr profile --build=missing")
    assert "mydep/1.0" in client.out
    assert "transitive/1.0 - Cache" not in client.out
    assert "transitive/1.0 - Build" not in client.out
    assert "transitive/1.0 - Missing" not in client.out

def test_replace_tool_requires():
    client = TestClient()
    client.save({
        "mytool/conanfile.py": GenConanfile("mytool", "1.0"),
        "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_tool_requires("tool/1.0"),
        "profile": "[replace_tool_requires]\ntool/*: mytool/1.0"
    })
    client.run("create mytool")
    client.run("create pkg -pr profile")
    assert "mytool/1.0" in client.out
    assert "tool/1.0 - Cache" not in client.out

def test_platform_requires_skip_binaries():
    client = TestClient()
    client.save({
        "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_require("sysdep/1.0"),
        "profile": "[platform_requires]\nsysdep/1.0"
    })
    # Since sysdep/1.0 is a platform require, it shouldn't try to download or build it
    # and it should show as "System tool"
    client.run("create pkg -pr profile")
    assert "sysdep/1.0 - System tool" in client.out
    assert "sysdep/1.0 - Missing" not in client.out

def test_replace_requires_different_name():
    # Test coverage includes an explicit case where a package is replaced with a structurally different name
    # to validate the dictionary rebuild logic.
    client = TestClient()
    client.save({
        "totally_different_name/conanfile.py": GenConanfile("totally_different_name", "1.0"),
        "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_require("original_name/1.0"),
        "profile": "[replace_requires]\noriginal_name/*: totally_different_name/1.0"
    })
    client.run("create totally_different_name")
    client.run("create pkg -pr profile")
    assert "totally_different_name/1.0" in client.out
    assert "original_name/1.0 - Cache" not in client.out


def test_replace_requires_multiple_and_mutation_regression():
    # Test that having multiple requires and replacing one does not corrupt the others,
    # ensuring the dictionary rebuild logic preserves all other requirements.
    client = TestClient()
    client.save({
        "mydep/conanfile.py": GenConanfile("mydep", "1.0"),
        "otherdep/conanfile.py": GenConanfile("otherdep", "1.0"),
        "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_require("dep/1.0").with_require("otherdep/1.0"),
        "profile": "[replace_requires]\ndep/*: mydep/1.0"
    })
    client.run("create mydep")
    client.run("create otherdep")
    client.run("create pkg -pr profile")
    assert "mydep/1.0" in client.out
    assert "otherdep/1.0" in client.out
    assert "dep/1.0 - Cache" not in client.out

def test_platform_requires_overrides_standard_node():
    # Validates that [platform_requires] correctly overrides a standard node (even if it exists
    # in the cache and has transitive dependencies), replacing it with a system tool node and
    # cutting off its transitive dependencies.
    client = TestClient()
    client.save({
        "pkg_c/conanfile.py": GenConanfile("pkg_c", "1.0"),
        "pkg_b/conanfile.py": GenConanfile("pkg_b", "1.0").with_require("pkg_c/1.0"),
        "pkg_a/conanfile.py": GenConanfile("pkg_a", "1.0").with_require("pkg_b/1.0"),
        "profile": "[platform_requires]\npkg_b/1.0"
    })
    client.run("create pkg_c")
    client.run("create pkg_b")
    client.run("create pkg_a -pr profile")
    
    assert "pkg_b/1.0 - System tool" in client.out
    assert "pkg_b/1.0 - Cache" not in client.out
    assert "pkg_c" not in client.out


def test_replace_requires_conflict_resolution():
    client = TestClient()
    client.save({
        "mydep/conanfile.py": GenConanfile("mydep", "1.0"),
        "dep/conanfile.py": GenConanfile("dep", "1.0"),
        "dep2/conanfile.py": GenConanfile("dep", "2.0"),
        "pkga/conanfile.py": GenConanfile("pkga", "1.0").with_require("dep/1.0"),
        "pkgb/conanfile.py": GenConanfile("pkgb", "1.0").with_require("dep/2.0"),
        "consumer/conanfile.py": """from conan import ConanFile
class Consumer(ConanFile):
    name = "consumer"
    version = "1.0"
    requires = "pkga/1.0", "pkgb/1.0"
    def generate(self):
        assert "mydep" in self.dependencies
        assert self.dependencies["mydep"].ref.name == "mydep"
        assert "dep" not in self.dependencies
""",
        "profile": "[replace_requires]\ndep/*: mydep/1.0"
    })
    client.run("create mydep")
    client.run("create dep")
    client.run("create dep2")
    client.run("create pkga")
    client.run("create pkgb")
    
    # Verify that without replace_requires it fails with conflict
    client.run("create consumer --build=missing", assert_error=True)
    assert "Conflict in pkga" in client.out or "conflict" in client.out.lower()
    
    # With replace_requires it succeeds
    client.run("create consumer -pr profile --build=missing")
    assert "mydep/1.0" in client.out
    assert "dep/1.0 - Cache" not in client.out
    assert "dep/2.0 - Cache" not in client.out

def test_replace_requires_transitive_lookup():
    # Test that a transitive dependency replaced by a profile override can be
    # correctly looked up by its new name in the consumer's generate() or build() method.
    client = TestClient()
    conanfile_pkg = """from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    requires = "dep/1.0"
    def generate(self):
        # We replaced 'transitive' with 'mydep', so we should be able to look it up
        assert "mydep" in self.dependencies
        assert self.dependencies["mydep"].ref.name == "mydep"
        # The original name should not be present
        assert "transitive" not in self.dependencies
"""
    client.save({
        "mydep/conanfile.py": GenConanfile("mydep", "1.0"),
        "dep/conanfile.py": GenConanfile("dep", "1.0").with_require("transitive/1.0"),
        "pkg/conanfile.py": conanfile_pkg,
        "profile": "[replace_requires]\ntransitive/*: mydep/1.0"
    })
    client.run("create mydep")
    client.run("export dep")
    client.run("create pkg -pr profile --build=missing")
    assert "mydep/1.0" in client.out
