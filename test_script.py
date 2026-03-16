import os
from conans.client.cache.cache import ClientCache

# mock global conf
class GlobalConf:
    def get(self, key):
        if key == "core.cache:storage_path":
            return "/tmp/non_existent_folder_xyz123"
        return None

try:
    c = ClientCache("/tmp/conan_home", GlobalConf())
    print("Success")
except Exception as e:
    print(f"Exception: {type(e)}: {e}")
