from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

def test():
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
    print(client.out)

test()
