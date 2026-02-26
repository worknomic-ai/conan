import pytest
from conans.test.utils.tools import TestClient
from conans.util.env import environment_update
from conans.test.assets.genconanfile import GenConanfile

class TestLogLevel:
    def test_default_log_level(self):
        t = TestClient()
        t.save({"conanfile.py": GenConanfile().with_package("self.output.debug('DEBUG MESSAGE')", 
                                                            "self.output.status('STATUS MESSAGE')")})
        t.run("create . --name=pkg --version=0.1")
        assert "STATUS MESSAGE" in t.out
        assert "DEBUG MESSAGE" not in t.out

    def test_env_var_override(self):
        t = TestClient()
        t.save({"conanfile.py": GenConanfile().with_package("self.output.debug('DEBUG MESSAGE')", 
                                                            "self.output.status('STATUS MESSAGE')")})
        with environment_update({"CONAN_LOG_LEVEL": "debug"}):
            t.run("create . --name=pkg --version=0.1")
        assert "STATUS MESSAGE" in t.out
        assert "DEBUG MESSAGE" in t.out

    def test_cli_precedence(self):
        t = TestClient()
        t.save({"conanfile.py": GenConanfile().with_package("self.output.debug('DEBUG MESSAGE')", 
                                                            "self.output.status('STATUS MESSAGE')")})
        # Env var says debug, but CLI says status
        with environment_update({"CONAN_LOG_LEVEL": "debug"}):
            t.run("create . --name=pkg --version=0.1 -vstatus")
        assert "STATUS MESSAGE" in t.out
        assert "DEBUG MESSAGE" not in t.out

        # Env var says status, but CLI says debug
        with environment_update({"CONAN_LOG_LEVEL": "status"}):
            t.run("create . --name=pkg --version=0.1 -vdebug")
        assert "STATUS MESSAGE" in t.out
        assert "DEBUG MESSAGE" in t.out

    def test_invalid_env_var(self):
        t = TestClient()
        with environment_update({"CONAN_LOG_LEVEL": "invalid"}):
            t.run("config list", assert_error=True)
        assert 'Invalid CONAN_LOG_LEVEL="invalid"' in t.out
