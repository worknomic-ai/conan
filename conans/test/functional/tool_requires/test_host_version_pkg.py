import textwrap
import pytest
from conans.test.utils.tools import TestClient

class TestHostVersionPkg:
    def test_host_version_pkg(self):
        c = TestClient()
        c.save({"dep/conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Dep(ConanFile):
                name = "dep"
                version = "1.0"
        """)})
        c.run("create dep")
        c.save({"dep/conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Dep(ConanFile):
                name = "dep"
                version = "1.1"
        """)})
        c.run("create dep")

        c.save({"tool/conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Tool(ConanFile):
                name = "tool"
        """)})
        c.run("create tool --version=1.0")
        c.run("create tool --version=1.1")

        pkg = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                name = "pkg"
                version = "0.1"
                def requirements(self):
                    self.requires("dep/1.1")
                def build_requirements(self):
                    self.tool_requires("tool/<host_version:dep>")
            """)
        c.save({"pkg/conanfile.py": pkg})
        c.run("install pkg")
        c.assert_listed_require({"dep/1.1": "Cache"})
        c.assert_listed_require({"tool/1.1": "Cache"}, build=True)

    def test_multiple_host_version_pkg(self):
        c = TestClient()
        c.save({"dep1/conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Dep1(ConanFile):
                name = "dep1"
                version = "1.0"
        """)})
        c.run("create dep1")
        c.save({"dep2/conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Dep2(ConanFile):
                name = "dep2"
                version = "2.0"
        """)})
        c.run("create dep2")

        c.save({"tool1/conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Tool1(ConanFile):
                name = "tool1"
        """)})
        c.run("create tool1 --version=1.0")
        c.save({"tool2/conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Tool2(ConanFile):
                name = "tool2"
        """)})
        c.run("create tool2 --version=2.0")

        pkg = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                name = "pkg"
                version = "0.1"
                def requirements(self):
                    self.requires("dep1/1.0")
                    self.requires("dep2/2.0")
                def build_requirements(self):
                    self.tool_requires("tool1/<host_version:dep1>")
                    self.tool_requires("tool2/<host_version:dep2>")
            """)
        c.save({"pkg/conanfile.py": pkg})
        c.run("install pkg")
        c.assert_listed_require({"dep1/1.0": "Cache"})
        c.assert_listed_require({"dep2/2.0": "Cache"})
        c.assert_listed_require({"tool1/1.0": "Cache"}, build=True)
        c.assert_listed_require({"tool2/2.0": "Cache"}, build=True)

    def test_host_version_pkg_not_found(self):
        c = TestClient()
        pkg = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                name = "pkg"
                version = "0.1"
                def build_requirements(self):
                    self.tool_requires("tool/<host_version:other>")
            """)
        c.save({"pkg/conanfile.py": pkg})
        c.run("install pkg", assert_error=True)
        assert "ERROR: pkg/0.1 require 'tool/<host_version:other>': didn't find a matching host dependency 'other'" in c.out

    def test_host_version_pkg_visible_error(self):
        c = TestClient()
        c.save({"dep/conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Dep(ConanFile):
                name = "dep"
                version = "1.0"
        """)})
        c.run("create dep")
        pkg = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                name = "pkg"
                version = "0.1"
                def requirements(self):
                    self.requires("dep/1.0")
                    self.requires("tool/<host_version:dep>")
            """)
        c.save({"pkg/conanfile.py": pkg})
        c.run("install pkg", assert_error=True)
        assert "ERROR: pkg/0.1 require 'tool/<host_version:dep>': 'host_version' can only be used for non-visible tool_requires" in c.out
