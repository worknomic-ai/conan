import os
import time
from conans.test.utils.tools import TestClient, GenConanfile

def test_missing_cache_folder():
    client = TestClient()
    client.save({"conanfile.py": GenConanfile("pkg", "0.1")})
    path = f"/tmp/unique_path_{int(time.time())}"
    client.save({"global.conf": f"core.cache:storage_path={path}"}, path=client.cache.cache_folder)
    
    # We assert that the command FAILS due to missing cache folder
    client.run("create .", assert_error=True)
    assert "Couldn't initialize storage" in client.out and "does not exist" in client.out

