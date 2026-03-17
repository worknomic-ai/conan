from conans.test.utils.tools import TestClient

def test_streams():
    client = TestClient()
    client.save({"conanfile.py": """
from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
"""})
    client.run("create conanfile.py")
    print("OUT:")
    print(repr(client.out))
    # print("STDOUT:")
    # print(repr(client.stdout))
    # print("STDERR:")
    # print(repr(client.stderr))
test_streams()
