import textwrap
import pytest
from conans.test.utils.tools import TestClient

class TestWarningsAsErrors:
    def test_warnings_as_errors_tag(self):
        client = TestClient()
        conanfile = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                def configure(self):
                    self.output.warning("This is a deprecated warning", warn_tag="deprecated")
            """)
        client.save({"conanfile.py": conanfile})

        # By default it is a warning
        client.run("graph info .")
        assert "WARN: deprecated: This is a deprecated warning" in client.out

        # Promoting to error
        client.save_home({"global.conf": "core:warnings_as_errors=['deprecated']"})
        client.run("graph info .", assert_error=True)
        assert "ConanException: deprecated: This is a deprecated warning" in client.out

    def test_warnings_as_errors_wildcard(self):
        client = TestClient()
        conanfile = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                def configure(self):
                    self.output.warning("This is some warning", warn_tag="mytag")
            """)
        client.save({"conanfile.py": conanfile})

        client.save_home({"global.conf": "core:warnings_as_errors=['*']"})
        client.run("graph info .", assert_error=True)
        assert "ConanException: mytag: This is some warning" in client.out

    def test_warnings_as_errors_no_match(self):
        client = TestClient()
        conanfile = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                def configure(self):
                    self.output.warning("This is some warning", warn_tag="mytag")
            """)
        client.save({"conanfile.py": conanfile})

        client.save_home({"global.conf": "core:warnings_as_errors=['other']"})
        client.run("graph info .")
        assert "WARN: mytag: This is some warning" in client.out

    def test_warnings_as_errors_silenced(self):
        client = TestClient()
        conanfile = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                def configure(self):
                    self.output.warning("This is some warning", warn_tag="mytag")
            """)
        client.save({"conanfile.py": conanfile})

        # If silenced, it should not raise error even if in warnings_as_errors
        # Note: core:skip_warnings is also a list
        client.save_home({"global.conf": textwrap.dedent("""
            core:warnings_as_errors=['mytag']
            core:skip_warnings=['mytag']
        """)})
        client.run("graph info .")
        assert "mytag: This is some warning" not in client.out
        assert "WARN: mytag" not in client.out

    def test_warnings_as_errors_multiple(self):
        client = TestClient()
        conanfile = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                def configure(self):
                    self.output.warning("warning1", warn_tag="tag1")
                    self.output.warning("warning2", warn_tag="tag2")
            """)
        client.save({"conanfile.py": conanfile})

        client.save_home({"global.conf": "core:warnings_as_errors=['tag1', 'tag3']"})
        client.run("graph info .", assert_error=True)
        assert "ConanException: tag1: warning1" in client.out
        assert "tag2: warning2" not in client.out
