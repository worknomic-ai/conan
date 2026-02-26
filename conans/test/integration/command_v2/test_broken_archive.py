
import os
from conan.api.conan_api import ConanAPI
from conan.api.model import PackagesList
from conan.api.subapi.cache import CacheAPI
from conans.errors import ConanException
from conans.test.utils.tools import TestClient
import tarfile
from io import BytesIO

def test_broken_archive_cleanup():
    c = TestClient()
    # Create a broken archive (missing pkglist.json)
    tgz_path = os.path.join(c.current_folder, "broken.tgz")
    with tarfile.open(tgz_path, "w:gz") as tar:
        pass # Empty archive
    
    # We need to call the API directly to see the error, or use c.run
    c.run("cache restore broken.tgz", assert_error=True)
    assert "pkglist.json not found in archive" in c.out
