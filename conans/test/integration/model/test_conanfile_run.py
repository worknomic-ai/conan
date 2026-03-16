from conans.test.utils.tools import TestClient

def test_conanfile_run_stderr():
    client = TestClient()
    conanfile = """
from conan import ConanFile
from io import StringIO
import sys

class Pkg(ConanFile):
    name = "pkg"
    version = "0.1"

    def build(self):
        stderr = StringIO()
        stdout = StringIO()
        # Use python to write reliably to stdout and stderr
        py_command = f'"{sys.executable}" -c "import sys; sys.stdout.write(\\'hello stdout\\'); sys.stderr.write(\\'hello stderr\\')"'
        self.run(py_command, stdout=stdout, stderr=stderr)
        self.output.info(f"CAPTURED STDOUT: {stdout.getvalue().strip()}")
        self.output.info(f"CAPTURED STDERR: {stderr.getvalue().strip()}")
"""
    client.save({"conanfile.py": conanfile})
    client.run("create .")
    assert "CAPTURED STDOUT: hello stdout" in client.out
    assert "CAPTURED STDERR: hello stderr" in client.out
