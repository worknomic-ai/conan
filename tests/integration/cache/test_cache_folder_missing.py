import os
from conans.test.utils.tools import TestClient, GenConanfile

def test_missing_cache_folder():
    client = TestClient()
    client.save({"conanfile.py": GenConanfile("pkg", "0.1")})
    client.save({"global.conf": "core.cache:storage_path=/nonexistent/path/for/conan/cache/xyz/abc"}, path=client.cache.cache_folder)
    client.run("create .", assert_error=True)
    assert "Cache folder" in client.out and "does not exist" in client.out
