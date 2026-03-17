from conan.api.conan_api import ConanAPI
import os

api = ConanAPI()
print(api.config.settings_yml[:100])
