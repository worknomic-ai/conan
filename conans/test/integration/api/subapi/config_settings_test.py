import textwrap
import pytest
import os
from conans.test.utils.tools import TestClient
from conans.errors import ConanException
from conan.api.conan_api import ConanAPI

def test_config_api_settings():
    client = TestClient()
    settings_yml = textwrap.dedent("""
        os: [Windows, Linux, Macos]
        compiler:
            gcc:
                version: ["11", "12"]
    """)
    settings_user_yml = textwrap.dedent("""
        os: [FreeBSD]
        my_custom_setting: [foo, bar]
    """)
    
    client.save_home({"settings.yml": settings_yml,
                      "settings_user.yml": settings_user_yml})
    
    # Access via API
    api = ConanAPI(client.cache_folder)
    
    # Test settings_yml
    settings = api.config.settings_yml
    assert settings["os"] == ["Windows", "Linux", "Macos"]
    assert settings["compiler"]["gcc"]["version"] == ["11", "12"]
    
    # Test settings_user
    settings_user = api.config.settings_user
    assert settings_user["os"] == ["FreeBSD"]
    assert settings_user["my_custom_setting"] == ["foo", "bar"]

def test_config_api_settings_missing():
    client = TestClient()
    # Ensure files are missing
    path = os.path.join(client.cache_folder, "settings.yml")
    if os.path.exists(path):
        os.remove(path)
    path_user = os.path.join(client.cache_folder, "settings_user.yml")
    if os.path.exists(path_user):
        os.remove(path_user)
    
    api = ConanAPI(client.cache_folder)
    assert api.config.settings_yml == {}
    assert api.config.settings_user == {}

def test_config_api_settings_malformed():
    client = TestClient()
    client.save_home({"settings.yml": "malformed: : yaml: "})
    
    api = ConanAPI(client.cache_folder)
    with pytest.raises(ConanException) as exc:
        _ = api.config.settings_yml
    assert "Error parsing settings.yml" in str(exc.value)

def test_config_api_settings_user_malformed():
    client = TestClient()
    client.save_home({"settings_user.yml": "malformed: : yaml: "})
    
    api = ConanAPI(client.cache_folder)
    with pytest.raises(ConanException) as exc:
        _ = api.config.settings_user
    assert "Error parsing settings_user.yml" in str(exc.value)
