import os
from conan.api.conan_api import ConanAPI
from conans.client.conf import default_settings_yml
from conans.test.utils.tools import TestClient

def test_config_settings_yml():
    client = TestClient()
    api = ConanAPI(cache_folder=client.cache_folder)
    
    # 1. Default settings.yml when file doesn't exist
    assert api.config.settings_yml == default_settings_yml
    
    # 2. Custom settings.yml
    custom_settings = "os: [Windows, Linux, Macos]\n"
    settings_path = os.path.join(client.cache_folder, "settings.yml")
    with open(settings_path, "w") as f:
        f.write(custom_settings)
        
    assert api.config.settings_yml == custom_settings
