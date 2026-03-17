import pytest
import textwrap
from conans.test.utils.tools import TestClient

def test_forced_download_source_with_tool_requires():
    c = TestClient(default_server_user=True)
    tool = textwrap.dedent("""
        from conan import ConanFile
        import os
        class Tool(ConanFile):
            name = "tool"
            version = "0.1"
            def package_info(self):
                self.buildenv_info.define("MYTOOL", "mytool_value")
    """)
    c.save({"tool/conanfile.py": tool})
    c.run("create tool")
    c.run("upload * -c -r=default")

    dep = textwrap.dedent("""
        from conan import ConanFile
        import os
        class Dep(ConanFile):
            name = "dep"
            version = "0.1"
            tool_requires = "tool/0.1"
            def source(self):
                self.output.info(f"MYTOOL IS: {os.environ.get('MYTOOL', 'NOT_SET')}")
                if os.environ.get('MYTOOL') != "mytool_value":
                    raise Exception("MYTOOL not set!")
    """)
    c.save({"dep/conanfile.py": dep})
    c.run("create dep")
    c.run("upload dep* -c -r=default")
    
    # Clean cache
    c.run("remove * -c")
    
    # Run install with forced download source
    c.run("install --requires=dep/0.1 -c tools.build:download_source=True")
    assert "MYTOOL IS: mytool_value" in c.out

def test_conan_source_command_no_graph():
    # conan source command does not build a graph, should not crash
    c = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        class Pkg(ConanFile):
            name = "pkg"
            version = "0.1"
            def source(self):
                self.output.info("Executing source!")
    """)
    c.save({"conanfile.py": conanfile})
    c.run("source .")
    assert "Executing source!" in c.out

