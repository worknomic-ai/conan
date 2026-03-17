import json

from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient


def test_lock_remove():
    client = TestClient()
    client.save({
        "pkg/conanfile.py": GenConanfile("pkg", "1.0"),
        "dep/conanfile.py": GenConanfile("dep", "1.0").with_requires("pkg/1.0"),
        "app/conanfile.py": GenConanfile("app", "1.0").with_requires("dep/1.0"),
    })
    
    # Create the packages
    client.run("create pkg")
    client.run("create dep")
    
    # Create the lockfile
    client.run("lock create app")
    
    lock_content = json.loads(client.load("app/conan.lock"))
    requires = lock_content["requires"]
    assert len(requires) == 2
    
    # Check that they exist
    assert any("pkg/1.0" in r for r in requires)
    assert any("dep/1.0" in r for r in requires)

    # Now we remove pkg/1.0
    client.run("lock remove --lockfile app/conan.lock --lockfile-out app/conan.lock --requires pkg/1.0")
    
    lock_content2 = json.loads(client.load("app/conan.lock"))
    requires2 = lock_content2["requires"]
    assert len(requires2) == 1
    assert any("dep/1.0" in r for r in requires2)
    assert not any("pkg/1.0" in r for r in requires2)
    
    # Check if removing non-existing requires works (or at least doesn't break)
    client.run("lock remove --lockfile app/conan.lock --lockfile-out app/conan.lock --requires unknown/1.0")
    lock_content3 = json.loads(client.load("app/conan.lock"))
    assert len(lock_content3["requires"]) == 1
    
    # Check removing another reference
    client.run("lock remove --lockfile app/conan.lock --lockfile-out app/conan.lock --requires dep/1.0")
    lock_content4 = json.loads(client.load("app/conan.lock"))
    assert len(lock_content4["requires"]) == 0

def test_lock_remove_build_requires():
    client = TestClient()
    client.save({
        "pkg/conanfile.py": GenConanfile("pkg", "1.0"),
        "tool/conanfile.py": GenConanfile("tool", "1.0").with_requires("pkg/1.0"),
        "app/conanfile.py": GenConanfile("app", "1.0").with_tool_requires("tool/1.0"),
    })
    
    client.run("create pkg")
    client.run("create tool")
    client.run("lock create app")
    
    lock_content = json.loads(client.load("app/conan.lock"))
    build_requires = lock_content["build_requires"]
    assert len(build_requires) == 2
    
    client.run("lock remove --lockfile app/conan.lock --lockfile-out app/conan.lock --build-requires pkg/1.0")
    
    lock_content2 = json.loads(client.load("app/conan.lock"))
    build_requires2 = lock_content2["build_requires"]
    assert len(build_requires2) == 1
    assert any("tool/1.0" in r for r in build_requires2)
    assert not any("pkg/1.0" in r for r in build_requires2)

def test_lock_remove_python_requires():
    client = TestClient()
    client.save({
        "pyreq/conanfile.py": GenConanfile("pyreq", "1.0"),
        "app/conanfile.py": GenConanfile("app", "1.0").with_python_requires("pyreq/1.0"),
    })
    
    client.run("create pyreq")
    client.run("lock create app")
    
    lock_content = json.loads(client.load("app/conan.lock"))
    python_requires = lock_content["python_requires"]
    assert len(python_requires) == 1
    
    client.run("lock remove --lockfile app/conan.lock --lockfile-out app/conan.lock --python-requires pyreq/1.0")
    
    lock_content2 = json.loads(client.load("app/conan.lock"))
    python_requires2 = lock_content2.get("python_requires", [])
    assert len(python_requires2) == 0

