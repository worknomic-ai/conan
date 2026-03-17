import pytest

from conans.test.utils.tools import TestClient

def test_warnings_as_errors_global():
    client = TestClient()
    client.save({"conanfile.py": """
from conan import ConanFile
from conan.api.output import ConanOutput

class Pkg(ConanFile):
    name = "pkg"
    version = "0.1"
    
    def source(self):
        ConanOutput().warning("This is a warning!", warn_tag="my_warning")
"""})
    client.run("source .")
    assert "WARN: my_warning: This is a warning!" in client.out
    
    # Enable global fail for this tag
    client.save({"global.conf": "core:warnings_as_errors=['my_warning']"}, path=client.cache.cache_folder)
    client.run("source .", assert_error=True)
    assert "my_warning: This is a warning!" in client.out or "ConanException" in client.out

    # Disable it in global.conf and use CLI
    client.save({"global.conf": ""}, path=client.cache.cache_folder)
    client.run("source . -c \"core:warnings_as_errors=['my_warning']\"", assert_error=True)

def test_warnings_as_errors_all():
    client = TestClient()
    client.save({"conanfile.py": """
from conan import ConanFile
from conan.api.output import ConanOutput

class Pkg(ConanFile):
    name = "pkg"
    version = "0.1"
    
    def source(self):
        ConanOutput().warning("This is a warning!")
"""})
    
    client.save({"global.conf": "core:warnings_as_errors=['all']"}, path=client.cache.cache_folder)
    client.run("source .", assert_error=True)

