import pytest
from conans.test.integration.graph.test_system_tools import save
from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

def test_platform_requires():
    client = TestClient()
    client.save({
        "conanfile.py": GenConanfile("pkg", "1.0").with_settings("os", "compiler", "build_type", "arch").with_require("dep/1.0").with_generator("CMakeDeps").with_generator("PkgConfigDeps"),
        "profile": "[platform_requires]\ndep/1.0"
    })
    client.run("install . -pr default -pr profile")
    print(client.out)
    assert "dep/1.0 - System tool" in client.out

def test_platform_tool_requires():
    client = TestClient()
    client.save({
        "conanfile.py": GenConanfile("pkg", "1.0").with_settings("os", "compiler", "build_type", "arch").with_tool_requires("tool/1.0").with_generator("CMakeDeps").with_generator("PkgConfigDeps"),
        "profile": "[platform_tool_requires]\ntool/1.0"
    })
    client.run("install . -pr default -pr profile")
    print(client.out)
    assert "tool/1.0 - System tool" in client.out

