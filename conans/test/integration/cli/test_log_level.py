import json

from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient
from conans.util.env import environment_update


def test_invalid_log_level_env_var():
    t = TestClient()
    t.save({"conanfile.py": GenConanfile()})
    with environment_update({"CONAN_LOG_LEVEL": "fooling"}):
        t.run("create . --name foo --version 1.0", assert_error=True)
        assert "Invalid log level 'fooling' in CONAN_LOG_LEVEL environment variable." in t.out


def test_log_level_env_var():
    lines = (
        "self.output.trace('This is a trace')",
        "self.output.debug('This is a debug')",
        "self.output.verbose('This is a verbose')",
        "self.output.info('This is a info')",
        "self.output.highlight('This is a highlight')",
        "self.output.success('This is a success')",
        "self.output.warning('This is a warning')",
        "self.output.error('This is a error')",
    )

    t = TestClient()
    t.save({"conanfile.py": GenConanfile().with_package(*lines)})

    # Default verbosity
    t.run("create . --name foo --version 1.0")
    assert "This is a trace" not in t.out
    assert "This is a debug" not in t.out
    assert "This is a verbose" not in t.out
    assert "This is a info" in t.out
    assert "This is a highlight" in t.out
    assert "This is a success" in t.out
    assert "This is a warning" in t.out
    assert "This is a error" in t.out

    # CONAN_LOG_LEVEL overrides default
    with environment_update({"CONAN_LOG_LEVEL": "verbose"}):
        t.run("create . --name foo --version 1.0")
        assert "This is a trace" not in t.out
        assert "This is a debug" not in t.out
        assert "This is a verbose" in t.out
        assert "This is a info" in t.out
        assert "This is a highlight" in t.out
        assert "This is a success" in t.out
        assert "This is a warning" in t.out
        assert "This is a error" in t.out

    # CLI flag dictates verbosity over CONAN_LOG_LEVEL
    with environment_update({"CONAN_LOG_LEVEL": "verbose"}):
        t.run("create . --name foo --version 1.0 -vwarning")
        assert "This is a trace" not in t.out
        assert "This is a debug" not in t.out
        assert "This is a verbose" not in t.out
        assert "This is a info" not in t.out
        assert "This is a highlight" not in t.out
        assert "This is a success" not in t.out
        assert "This is a warning" in t.out
        assert "This is a error" in t.out

def test_log_level_stdout_stderr_isolation():
    t = TestClient()
    conanfile = """from conan import ConanFile
class Pkg(ConanFile):
    name = "foo"
    version = "1.0"
    def configure(self):
        self.output.info('This is a info log message!')
        self.output.warning('This is a warning log message!')
"""
    t.save({"conanfile.py": conanfile})
    
    # We test `conan graph info` because it produces formatted output on stdout
    # and we want to ensure logs go to stderr.
    with environment_update({"CONAN_LOG_LEVEL": "verbose"}):
        t.run("graph info . --format json")
        
        # Verify strict separation
        assert "This is a info log message!" in t.stderr
        assert "This is a warning log message!" in t.stderr
        assert "This is a info log message!" not in t.stdout
        assert "This is a warning log message!" not in t.stdout

        # Verify formatted output on stdout
        assert "graph" in t.stdout
        # Test that JSON is valid
        data = json.loads(t.stdout)
        assert "graph" in data
