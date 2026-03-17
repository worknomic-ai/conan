import os
import textwrap
from conans.test.utils.tools import TestClient

c = TestClient()

conanfile = textwrap.dedent("""
    import os
    from conan import ConanFile
    from conan.tools.files import load
    class Lib(ConanFile):
        name = "pkg"
        version = "0.1"
        def set_version(self):
            self.user = "myuser"
            self.channel = "mychannel"
    """)
c.save({"conanfile.py": conanfile})
c.run("export .")
print(c.out)
