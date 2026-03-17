from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

client = TestClient()
client.save({
    "mydep/conanfile.py": GenConanfile("mydep", "1.0"),
    "pkg/conanfile.py": GenConanfile("pkg", "1.0").with_require("dep/1.0"),
    "profile": "[replace_requires]\ndep/*: mydep/1.0"
})
client.run("create mydep")
client.run("create pkg -pr profile")
print(client.out)
