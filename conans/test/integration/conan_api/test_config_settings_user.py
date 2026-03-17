import os
import textwrap

from conans.test.utils.tools import TestClient
from conan.api.conan_api import ConanAPI

def test_config_settings_user():
    client = TestClient()
    conan_api = ConanAPI(cache_folder=client.cache_folder)
    
    # Ensure it's empty when file doesn't exist
    assert conan_api.config.settings_user == ""

    # Create file
    settings_user = textwrap.dedent("""\
        os:
            Windows:
                subsystem: [msys2, cygwin]
        """)
    client.save({"settings_user.yml": settings_user}, path=client.cache_folder)
    
    # Ensure it reads the correct file
    assert conan_api.config.settings_user == settings_user
