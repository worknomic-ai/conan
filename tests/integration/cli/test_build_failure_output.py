import os
from conans.test.utils.tools import TestClient

def test_build_failure_no_migration_warning():
    client = TestClient()
    conanfile = """
from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    def build(self):
        self.run("false")  # simulate build failure
"""
    client.save({"conanfile.py": conanfile})
    client.run("create .", assert_error=True)
    
    # Assert that the migration warning is not in the output
    assert "It is possible that this recipe is not Conan 2.0 ready" not in client.out
    assert "Running 2.0.14 Cache DB migration" not in client.out

test_build_failure_no_migration_warning()
