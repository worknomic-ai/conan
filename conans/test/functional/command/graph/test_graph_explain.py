import textwrap
import pytest
from conans.test.utils.tools import TestClient, TestServer

class TestGraphExplain:
    def test_graph_explain_remotes(self):
        client = TestClient(default_server_user=True)
        client.save({"conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                name = "pkg"
                version = "0.1"
        """)})
        client.run("create .")
        client.run("upload pkg/0.1 -r default")
        client.run("remove pkg/0.1:#* -c") # Remove binary from cache

        # Add a second remote
        server2 = TestServer()
        client.servers["remote2"] = server2
        client.run("remote add remote2 " + server2.fake_url)
        
        client.run("graph explain --requires=pkg/0.1 -r remote2 -r default")
        assert "Binary Selection explanation:" in client.out
        assert "pkg/0.1:" in client.out
        assert "Remote 'remote2' check for" in client.out
        assert "not found" in client.out
        assert "Remote 'default' check for" in client.out
        assert "found" in client.out.lower()
        
    def test_graph_explain_lockfile_override(self):
        client = TestClient()
        client.save({"conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                pass
        """)})
        client.run("create . --name=pkg --version=0.1")
        client.run("create . --name=pkg --version=0.2")
        
        client.save({"consumer.py": textwrap.dedent("""
            from conan import ConanFile
            class Consumer(ConanFile):
                requires = "pkg/[>=0.1]"
        """)})
        
        # Create a lockfile that forces 0.1
        client.run("lock create --requires=pkg/0.1 --lockfile-out=conan.lock")
        
        client.run("graph explain consumer.py --lockfile=conan.lock")
        # When using a lockfile, the version is locked
        assert "pkg/0.1" in client.out
        assert "pkg/0.2" not in client.out

    def test_graph_explain_range(self):
        client = TestClient()
        client.save({"conanfile.py": "from conan import ConanFile\nclass Pkg(ConanFile): pass"})
        client.run("create . --name=pkg --version=0.1")
        client.run("graph explain --requires=pkg/[>0.0]")
        assert "Resolved version ranges:" in client.out
        assert "pkg/[>0.0] -> pkg/0.1" in client.out

    def test_graph_explain_compatible(self):

        client = TestClient()
        # Create a package with a specific setting
        client.save({"conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                name = "pkg"
                version = "0.1"
                settings = "os"
        """)})
        client.run("create . -s os=Linux")
        
        # Now try to use it from a consumer with os=Windows but add compatibility
        # We can use the compatibility.py plugin
        compatibility_py = textwrap.dedent("""
            def compatibility(conanfile):
                if conanfile.settings.os == "Windows":
                    return [{"settings": [("os", "Linux")]}]
                return []
        """)
        client.save_home({"extensions/plugins/compatibility/compatibility.py": compatibility_py})
        
        client.run("graph explain --requires=pkg/0.1 -s os=Windows")
        assert "Checking compatible packages..." in client.out
        assert "Compatible" in client.out
        # In Conan 2.x, the output of graph explain shows the status of compatible check
        assert "Cache" in client.out

    def test_graph_explain_invalid(self):
        client = TestClient()
        client.save({"conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            from conan.errors import ConanInvalidConfiguration
            class Pkg(ConanFile):
                name = "pkg"
                version = "0.1"
                settings = "os"
                def validate(self):
                    if self.settings.os == "Windows":
                        raise ConanInvalidConfiguration("Windows is not supported!")
        """)})
        client.run("create . -s os=Linux")
        client.run("graph explain --requires=pkg/0.1 -s os=Windows")
        assert "pkg/0.1" in client.out
        assert "Binary: Invalid" in client.out
        assert "Invalid configuration: Windows is not supported!" in client.out

    def test_graph_explain_validate_build(self):
        client = TestClient()
        client.save({"conanfile.py": textwrap.dedent("""
            from conan import ConanFile
            from conan.errors import ConanInvalidConfiguration
            class Pkg(ConanFile):
                name = "pkg"
                version = "0.1"
                settings = "os"
                def validate_build(self):
                    if self.settings.os == "Windows":
                        raise ConanInvalidConfiguration("Cannot build on Windows!")
        """)})
        client.run("export .")
        client.run("graph explain --requires=pkg/0.1 -s os=Windows --build=missing")
        assert "pkg/0.1" in client.out
        assert "Binary: Invalid" in client.out
        assert "Invalid build: Cannot build on Windows!" in client.out

