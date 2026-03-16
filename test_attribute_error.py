from conans.test.utils.tools import TestClient
client = TestClient()
client.save({"global.conf": "core.sources:download_urls=['origin']\n"}, path=client.cache.cache_folder)
conanfile = """from conan import ConanFile
from conan.tools.files import download
class Pkg(ConanFile):
   def source(self):
       download(self, "http://localhost:5000/myfile.txt", "myfile.txt", sha256="d9014c4624844aa5bac314773d6b689ad467fa4e1d1a50a1b8a99d5a95f72ff5")
"""
client.save({"conanfile.py": conanfile})
try:
    client.run("source .")
except Exception as e:
    import traceback
    traceback.print_exc()
