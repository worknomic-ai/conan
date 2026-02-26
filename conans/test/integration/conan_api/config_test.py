import pytest
import os
from conan.api.conan_api import ConanAPI
from conans.errors import ConanException
from conans.test.utils.tools import TestClient

def test_config_settings_yml():
    client = TestClient()
    api = ConanAPI(client.cache_folder)
    
    # Test valid settings.yml
    settings_content = "os: [Windows, Linux]\ncompiler: [gcc, clang]"
    client.save_home({"settings.yml": settings_content})
    assert api.config.settings_yml == {"os": ["Windows", "Linux"], "compiler": ["gcc", "clang"]}

def test_config_settings_user():
    client = TestClient()
    api = ConanAPI(client.cache_folder)
    
    # Test valid settings_user.yml
    settings_user_content = "my_setting: [value1, value2]"
    client.save_home({"settings_user.yml": settings_user_content})
    assert api.config.settings_user == {"my_setting": ["value1", "value2"]}

def test_config_settings_missing():
    client = TestClient()
    # TestClient creates settings.yml by default, so we remove it
    os.remove(os.path.join(client.cache_folder, "settings.yml"))
    api = ConanAPI(client.cache_folder)
    
    # Test missing files
    assert api.config.settings_yml == {}
    assert api.config.settings_user == {}

def test_config_settings_malformed():
    client = TestClient()
    api = ConanAPI(client.cache_folder)
    
    # Test malformed settings.yml
    client.save_home({"settings.yml": "os: [Windows, Linux"})
    with pytest.raises(ConanException) as exc:
        _ = api.config.settings_yml
    assert "Error parsing settings.yml" in str(exc.value)

    # Test malformed settings_user.yml
    client.save_home({"settings_user.yml": "my_setting: [value1, value2"})
    with pytest.raises(ConanException) as exc:
        _ = api.config.settings_user
    assert "Error parsing settings_user.yml" in str(exc.value)
