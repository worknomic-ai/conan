import os
from conan.api.conan_api import ConanAPI

api = ConanAPI()

user_settings = api.config.settings_user
print("user settings:", user_settings)
