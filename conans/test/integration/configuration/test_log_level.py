import pytest
from conans.test.utils.tools import TestClient

def test_log_level_env_var():
    client = TestClient()
    client.save({"conanfile.py": "from conan import ConanFile\nclass Pkg(ConanFile):\n    name = 'pkg'\n    version = '1.0'"})
    
    import os
    os.environ["CONAN_LOG_LEVEL"] = "invalid_level"
    try:
        client.run("create .", assert_error=True)
        assert "Environment variable 'CONAN_LOG_LEVEL' has invalid value: 'invalid_level'" in client.out
    finally:
        del os.environ["CONAN_LOG_LEVEL"]

    os.environ["CONAN_LOG_LEVEL"] = "debug"
    try:
        client.run("create .")
        assert "pkg/1.0: Created package" in client.out
    finally:
        del os.environ["CONAN_LOG_LEVEL"]

    os.environ["CONAN_LOG_LEVEL"] = "error"
    try:
        client.run("create . -vtrace")
        assert "Created package" in client.out
    finally:
        del os.environ["CONAN_LOG_LEVEL"]
