import os

with open("conan/api/subapi/config.py", "r") as f:
    content = f.read()

new_prop = """
    @property
    def settings_user(self):
        cache_folder = self.conan_api.cache_folder
        home_paths = HomePaths(cache_folder)
        settings_user_path = home_paths.settings_path_user
        if os.path.exists(settings_user_path):
            return load(settings_user_path)
        return ""
"""

content = content + new_prop

with open("conan/api/subapi/config.py", "w") as f:
    f.write(content)
