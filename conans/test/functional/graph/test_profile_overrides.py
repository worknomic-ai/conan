import pytest
from conans.test.utils.tools import TestClient, GenConanfile

def test_replace_requires():
    client = TestClient()
    # Let's create a diamond dependency or transitive conflict
    client.save({
        "dep/1.0/conanfile.py": GenConanfile("dep", "1.0"),
        "dep/2.0/conanfile.py": GenConanfile("dep", "2.0"),
        "pkg_a/conanfile.py": GenConanfile("pkg_a", "1.0").with_require("dep/1.0"),
        "pkg_b/conanfile.py": GenConanfile("pkg_b", "1.0").with_require("dep/2.0"),
        "app/conanfile.py": GenConanfile("app", "1.0").with_require("pkg_a/1.0").with_require("pkg_b/1.0"),
    })
    
    client.run("create dep/1.0/")
    client.run("create dep/2.0/")
    client.run("create pkg_a/")
    client.run("create pkg_b/")
    
    # Without override, it should fail due to conflict
    client.run("create app/ --build=missing", assert_error=True)
    assert "Conflict in pkg_a/1.0" in client.out or "Conflict in app/1.0" in client.out or "conflict" in client.out.lower()
    
    # Now use replace_requires to resolve the conflict
    profile = """
[replace_requires]
dep/*: dep/2.0
"""
    client.save({"profile": profile})
    client.run("create app/ -pr profile --build=missing")
    assert "dep/2.0" in client.out
    assert "Conflict" not in client.out
    assert "dep/2.0: Already installed" in client.out or "dep/2.0: Built" in client.out or "dep/2.0: Cache" in client.out
    assert "app/1.0: Created package" in client.out

def test_replace_tool_requires():
    client = TestClient()
    client.save({
        "tool/1.0/conanfile.py": GenConanfile("tool", "1.0"),
        "tool/2.0/conanfile.py": GenConanfile("tool", "2.0"),
        "app/conanfile.py": GenConanfile("app", "1.0").with_build_requires("tool/1.0"),
    })
    
    client.run("create tool/1.0/")
    client.run("create tool/2.0/")
    
    # Without override, tool/1.0 is used
    client.run("create app/ --build=missing")
    assert "tool/1.0" in client.out
    
    # With replace_tool_requires, tool/2.0 is used
    profile = """
[replace_tool_requires]
tool/*: tool/2.0
"""
    client.save({"profile": profile})
    # Force build to actually check tool_requires
    client.run("create app/ -pr profile --build=app*")
    assert "tool/2.0" in client.out
    assert "tool/2.0: Already installed" in client.out or "tool/2.0 - Cache" in client.out
    assert "app/1.0: Created package" in client.out

def test_platform_requires():
    client = TestClient()
    client.save({
        "app/conanfile.py": GenConanfile("app", "1.0").with_require("zlib/1.2.11"),
    })
    
    # Normally it fails to find zlib/1.2.11
    client.run("create app/ --build=missing", assert_error=True)
    assert "not resolved" in client.out or "not found" in client.out.lower()
    
    # With platform_requires, it pretends zlib is already installed by the platform
    profile = """
[platform_requires]
zlib/1.2.11
"""
    client.save({"profile": profile})
    client.run("create app/ -pr profile --build=missing")
    assert "zlib/1.2.11 - Platform" in client.out or "zlib/1.2.11 - System tool" in client.out or "zlib/1.2.11 - Provided" in client.out
    assert "app/1.0: Created package" in client.out

def test_system_tools_deprecation():
    client = TestClient()
    client.save({
        "app/conanfile.py": GenConanfile("app", "1.0"),
    })
    
    profile = """
[system_tools]
cmake/3.20
"""
    client.save({"profile": profile})
    client.run("create app/ -pr profile --build=missing")
    assert "[system_tools] is deprecated in profiles, use [platform_tool_requires] instead." in client.out
