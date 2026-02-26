import textwrap
from conans.test.utils.tools import TestClient, GenConanfile

class TestProfileOverrides:
    def test_replace_requires(self):
        c = TestClient()
        c.save({"dep1/conanfile.py": GenConanfile("dep1", "0.1"),
                "dep2/conanfile.py": GenConanfile("dep2", "0.2"),
                "pkg/conanfile.py": GenConanfile("pkg", "0.1").with_requires("dep1/0.1")})
        c.run("create dep1")
        c.run("create dep2")

        profile = textwrap.dedent("""
            [replace_requires]
            dep1/0.1: dep2/0.2
        """)
        c.save({"myprofile": profile})
        c.run("graph info pkg -pr=myprofile")
        assert "dep1/0.1" not in c.out
        assert "dep2/0.2" in c.out
        # Verify it is actually using dep2/0.2 from cache
        c.assert_listed_require({"dep2/0.2": "Cache"})

    def test_platform_requires(self):
        c = TestClient()
        # dep/0.1 does NOT exist in cache
        c.save({"pkg/conanfile.py": GenConanfile("pkg", "0.1").with_requires("dep/0.1")})

        # This should fail normally
        c.run("graph info pkg", assert_error=True)
        assert "not resolved" in c.out

        profile = textwrap.dedent("""
            [platform_requires]
            dep/0.1
        """)
        c.save({"myprofile": profile})
        c.run("graph info pkg -pr=myprofile")
        c.assert_listed_require({"dep/0.1": "Platform"})

    def test_profile_composition(self):
        c = TestClient()
        c.save({"dep1/conanfile.py": GenConanfile("dep1", "0.1"),
                "dep2/conanfile.py": GenConanfile("dep2", "0.2"),
                "pkg/conanfile.py": GenConanfile("pkg", "0.1").with_requires("dep1/0.1")
                                                              .with_requires("base/0.1")})
        c.run("create dep1")
        c.run("create dep2")
        # base/0.1 is platform

        pr1 = textwrap.dedent("""
            [replace_requires]
            dep1/0.1: dep2/0.2
        """)
        pr2 = textwrap.dedent("""
            [platform_requires]
            base/0.1
        """)
        c.save({"pr1": pr1, "pr2": pr2})
        c.run("graph info pkg -pr=pr1 -pr=pr2")
        c.assert_listed_require({"dep2/0.2": "Cache",
                                 "base/0.1": "Platform"})

    def test_replace_platform_requires_combined(self):
        c = TestClient()
        c.save({"pkg/conanfile.py": GenConanfile("pkg", "0.1").with_requires("dep1/0.1")})

        # dep1/0.1 -> dep2/0.2 (which is platform)
        profile = textwrap.dedent("""
            [replace_requires]
            dep1/0.1: dep2/0.2
            [platform_requires]
            dep2/0.2
        """)
        c.save({"myprofile": profile})
        c.run("graph info pkg -pr=myprofile")
        assert "dep1/0.1" not in c.out
        c.assert_listed_require({"dep2/0.2": "Platform"})
