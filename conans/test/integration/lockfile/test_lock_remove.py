import json
import textwrap

from conans.test.utils.tools import TestClient


class TestLockRemove:
    def test_lock_remove_requires(self):
        c = TestClient()
        c.run("lock add --requires=pkg/0.1 --requires=dep/0.1 --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert len(lock["requires"]) == 2

        c.run("lock remove --requires=pkg/0.1 --lockfile=conan.lock --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert len(lock["requires"]) == 1
        assert "pkg/0.1" not in lock["requires"][0]
        assert "dep/0.1" in lock["requires"][0]

    def test_lock_remove_build_requires(self):
        c = TestClient()
        c.run("lock add --build-requires=tool/1.0 --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert "tool/1.0" in lock["build_requires"][0]

        c.run("lock remove --build-requires=tool/1.0 --lockfile=conan.lock --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert not lock.get("build_requires")

    def test_lock_remove_python_requires(self):
        c = TestClient()
        c.run("lock add --python-requires=pytool/1.0 --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert "pytool/1.0" in lock["python_requires"][0]

        c.run("lock remove --python-requires=pytool/1.0 --lockfile=conan.lock --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert not lock.get("python_requires")

    def test_lock_remove_no_revision_matches_revision(self):
        c = TestClient()
        c.run("lock add --requires=pkg/0.1#revision1 --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert "pkg/0.1#revision1" in lock["requires"][0]

        c.run("lock remove --requires=pkg/0.1 --lockfile=conan.lock --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert not lock.get("requires")

    def test_lock_remove_non_existent(self):
        c = TestClient()
        c.run("lock add --requires=pkg/0.1 --lockfile-out=conan.lock")
        c.run("lock remove --requires=non_existent/1.0 --lockfile=conan.lock --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert len(lock["requires"]) == 1
        assert "pkg/0.1" in lock["requires"][0]

    def test_lock_remove_multiple(self):
        c = TestClient()
        c.run("lock add --requires=pkg/0.1 --requires=dep/0.1 --requires=other/0.1 --lockfile-out=conan.lock")
        c.run("lock remove --requires=pkg/0.1 --requires=dep/0.1 --lockfile=conan.lock --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert len(lock["requires"]) == 1
        assert "other/0.1" in lock["requires"][0]

    def test_lock_remove_all_types(self):
        c = TestClient()
        c.run("lock add --requires=pkg/0.1 --build-requires=tool/1.0 --python-requires=pytool/1.0 --lockfile-out=conan.lock")
        c.run("lock remove --requires=pkg/0.1 --build-requires=tool/1.0 --python-requires=pytool/1.0 --lockfile=conan.lock --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert not lock.get("requires")
        assert not lock.get("build_requires")
        assert not lock.get("python_requires")

    def test_lock_remove_no_lockfile_error(self):
        c = TestClient()
        c.run("lock remove --requires=pkg/0.1", assert_error=True)
        assert "ERROR: A lockfile is required to remove requirements" in c.out

    def test_lock_remove_multiple_revisions(self):
        c = TestClient()
        c.run("lock add --requires=pkg/0.1#rev1 --requires=pkg/0.1#rev2 --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert len(lock["requires"]) == 2

        c.run("lock remove --requires=pkg/0.1 --lockfile=conan.lock --lockfile-out=conan.lock")
        lock = json.loads(c.load("conan.lock"))
        assert not lock.get("requires")
