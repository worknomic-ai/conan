from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

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

