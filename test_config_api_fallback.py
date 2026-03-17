from conan.api.conan_api import ConanAPI
import os

api = ConanAPI(cache_folder="/tmp/empty_cache")
print(api.config.settings_yml[:100])
