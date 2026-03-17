import pytest
from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

def test_platform_requires_options():
    client = TestClient()
    conanfile = GenConanfile("pkg", "1.0")
    conanfile.with_setting("os")
    conanfile.with_requirement("dep/1.0", options={"shared": True})
    client.save({
        "conanfile.py": conanfile,
        "profile": "[platform_requires]\ndep/1.0"
    })
    client.run("install . -pr profile -s os=Linux")
    print(client.out)
    assert "dep/1.0 - System tool" in client.out

