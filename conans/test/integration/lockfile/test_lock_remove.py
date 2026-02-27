import json
import pytest
from conans.test.utils.tools import TestClient, GenConanfile

class TestLockRemove:

    def test_lock_remove_requires(self):
        client = TestClient()
        client.save({"pkg/conanfile.py": GenConanfile("pkg", "0.1"),
                     "consumer/conanfile.txt": "[requires]\npkg/0.1"})
        client.run("create pkg")
        client.run("lock create consumer/conanfile.txt --lockfile-out=conan.lock")
        lock = client.load("conan.lock")
        assert "pkg/0.1" in lock

        client.run("lock remove --requires=pkg/0.1")
        lock = client.load("conan.lock")
        assert "pkg/0.1" not in lock

    def test_lock_remove_build_requires(self):
        client = TestClient()
        client.save({"tool/conanfile.py": GenConanfile("tool", "0.1"),
                     "consumer/conanfile.txt": "[tool_requires]\ntool/0.1"})
        client.run("create tool")
        client.run("lock create consumer/conanfile.txt --lockfile-out=conan.lock")
        lock = client.load("conan.lock")
        assert "tool/0.1" in lock

        client.run("lock remove --build-requires=tool/0.1")
        lock = client.load("conan.lock")
        assert "tool/0.1" not in lock

    def test_lock_remove_python_requires(self):
        client = TestClient()
        client.save({"pyreq/conanfile.py": GenConanfile("pyreq", "0.1"),
                     "consumer/conanfile.py": GenConanfile().with_python_requires("pyreq/0.1")})
        client.run("export pyreq")
        client.run("lock create consumer/conanfile.py --lockfile-out=conan.lock")
        lock = client.load("conan.lock")
        assert "pyreq/0.1" in lock

        client.run("lock remove --python-requires=pyreq/0.1")
        lock = client.load("conan.lock")
        assert "pyreq/0.1" not in lock

    def test_lock_remove_specific_revision(self):
        client = TestClient()
        client.save({"pkg/conanfile.py": GenConanfile("pkg", "0.1"),
                     "consumer/conanfile.txt": "[requires]\npkg/0.1"})
        client.run("create pkg")
        client.run("lock create consumer/conanfile.txt --lockfile-out=conan.lock")
        
        lock_json = json.loads(client.load("conan.lock"))
        pkg_ref = lock_json["requires"][0]
        if isinstance(pkg_ref, list): 
             pkg_ref = pkg_ref[0]
             
        client.run(f"lock remove --requires={pkg_ref}")
        lock = client.load("conan.lock")
        assert "pkg/0.1" not in lock

    def test_lock_remove_wrong_revision(self):
        client = TestClient()
        client.save({"pkg/conanfile.py": GenConanfile("pkg", "0.1"),
                     "consumer/conanfile.txt": "[requires]\npkg/0.1"})
        client.run("create pkg")
        client.run("lock create consumer/conanfile.txt --lockfile-out=conan.lock")
        
        client.run("lock remove --requires=pkg/0.1#fakerevision")
        lock = client.load("conan.lock")
        assert "pkg/0.1" in lock 

    def test_lock_remove_missing_lockfile(self):
        client = TestClient()
        client.run("lock remove --requires=pkg/0.1", assert_error=True)
        assert "Lockfile doesn't exist" in client.out
