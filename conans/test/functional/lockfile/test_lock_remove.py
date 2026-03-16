from conans.test.utils.tools import TestClient
from conans.test.assets.genconanfile import GenConanfile

def test_lock_remove_requires():
    client = TestClient()
    client.save({
        "dep/conanfile.py": GenConanfile("dep"),
        "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_requires("dep/[>=1.0]"),
    })

    # Create dep/1.0
    client.run("create dep/conanfile.py --version=1.0")

    # Create lockfile for pkg, locking dep to 1.0
    client.run("lock create pkg/conanfile.py --lockfile-out=conan.lock")
    assert "dep/1.0" in client.out

    # Create dep/2.0
    client.run("create dep/conanfile.py --version=2.0")

    # Install pkg with lockfile - should resolve to dep/1.0
    client.run("install pkg/conanfile.py --lockfile=conan.lock")
    assert "dep/1.0" in client.out
    assert "dep/2.0" not in client.out

    # Remove dep from lockfile
    client.run("lock remove --requires=dep/* --lockfile=conan.lock --lockfile-out=conan.lock")

    # Install pkg with modified lockfile - should resolve to dep/2.0
    # Note: --lockfile-partial is required since we removed a requirement but it is still in the recipe
    client.run("install pkg/conanfile.py --lockfile=conan.lock --lockfile-partial")
    assert "dep/2.0" in client.out

def test_lock_remove_build_requires():
    client = TestClient()
    client.save({
        "tool/conanfile.py": GenConanfile("tool"),
        "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_build_requires("tool/[>=1.0]"),
    })

    # Create tool/1.0
    client.run("create tool/conanfile.py --version=1.0")

    # Create lockfile for pkg, locking tool to 1.0
    client.run("lock create pkg/conanfile.py --lockfile-out=conan.lock")
    assert "tool/1.0" in client.out

    # Create tool/2.0
    client.run("create tool/conanfile.py --version=2.0")

    # Install pkg with lockfile - should resolve to tool/1.0
    client.run("install pkg/conanfile.py --lockfile=conan.lock --build=missing")
    assert "tool/1.0" in client.out
    assert "tool/2.0" not in client.out

    # Remove tool from lockfile
    client.run("lock remove --build-requires=tool/* --lockfile=conan.lock --lockfile-out=conan.lock")

    # Install pkg with modified lockfile - should resolve to tool/2.0
    client.run("install pkg/conanfile.py --lockfile=conan.lock --lockfile-partial --build=missing")
    assert "tool/2.0" in client.out

def test_lock_remove_python_requires():
    client = TestClient()
    client.save({
        "pytool/conanfile.py": GenConanfile("pytool"),
        "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_python_requires("pytool/[>=1.0]"),
    })

    # Create pytool/1.0
    client.run("create pytool/conanfile.py --version=1.0")

    # Create lockfile for pkg, locking pytool to 1.0
    client.run("lock create pkg/conanfile.py --lockfile-out=conan.lock")
    assert "pytool/1.0" in client.out

    # Create pytool/2.0
    client.run("create pytool/conanfile.py --version=2.0")

    # Install pkg with lockfile - should resolve to pytool/1.0
    client.run("install pkg/conanfile.py --lockfile=conan.lock")
    assert "pytool/1.0" in client.out
    assert "pytool/2.0" not in client.out

    # Remove pytool from lockfile
    client.run("lock remove --python-requires=pytool/* --lockfile=conan.lock --lockfile-out=conan.lock")

    # Install pkg with modified lockfile - should resolve to pytool/2.0
    client.run("install pkg/conanfile.py --lockfile=conan.lock --lockfile-partial")
    assert "pytool/2.0" in client.out

def test_lock_remove_non_existent():
    client = TestClient()
    client.save({
        "dep/conanfile.py": GenConanfile("dep", "1.0"),
        "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_requires("dep/[>=1.0]"),
    })
    
    client.run("create dep/conanfile.py")
    client.run("lock create pkg/conanfile.py --lockfile-out=conan.lock")
    
    # Remove a non-existent requirement
    client.run("lock remove --requires=nonexistent/* --lockfile=conan.lock --lockfile-out=conan.lock")
    
    # Verify no error and gracefully generated
    assert "Generated lockfile:" in client.out
