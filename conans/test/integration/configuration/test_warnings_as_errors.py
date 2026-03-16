import pytest

from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

def test_warnings_as_errors_unknown():
    client = TestClient()
    conanfile = """from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    def generate(self):
        self.output.warning("This is a warning without a tag")
"""
    client.save({"conanfile.py": conanfile})
    
    # Test normal warning
    client.run("create .")
    assert "WARN: This is a warning without a tag" in client.out
    
    # Test warnings_as_errors=unknown
    client.save({"global.conf": "core:warnings_as_errors=['unknown']"}, path=client.cache.cache_folder)
    client.run("create .", assert_error=True)
    assert "ERROR: This is a warning without a tag" in client.out or "This is a warning without a tag" in client.out

def test_warnings_as_errors_all():
    client = TestClient()
    conanfile = """from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    def generate(self):
        self.output.warning("This is a warning without a tag")
"""
    client.save({"conanfile.py": conanfile})
    
    # Test warnings_as_errors=all
    client.save({"global.conf": "core:warnings_as_errors=['all']"}, path=client.cache.cache_folder)
    client.run("create .", assert_error=True)
    assert "This is a warning without a tag" in client.out

def test_warnings_as_errors_tag():
    client = TestClient()
    conanfile = """from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    def generate(self):
        self.output.warning("This is a warning with a tag", warn_tag="my_tag")
"""
    client.save({"conanfile.py": conanfile})
    
    # Test normal warning
    client.run("create .")
    assert "WARN: my_tag: This is a warning with a tag" in client.out
    
    # Test unknown tag (should not raise)
    client.save({"global.conf": "core:warnings_as_errors=['other_tag']"}, path=client.cache.cache_folder)
    client.run("create .")
    assert "WARN: my_tag: This is a warning with a tag" in client.out
    
    # Test specific tag
    client.save({"global.conf": "core:warnings_as_errors=['my_tag']"}, path=client.cache.cache_folder)
    client.run("create .", assert_error=True)
    assert "my_tag: This is a warning with a tag" in client.out
