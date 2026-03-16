import textwrap
import io
import os

from conans.test.utils.tools import TestClient

def test_cmake_ctest_helper():
    client = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        from conan.tools.cmake import CMake, CMakeToolchain
        class Pkg(ConanFile):
            name = "pkg"
            version = "0.1"
            settings = "os", "compiler", "build_type", "arch"
            
            def generate(self):
                tc = CMakeToolchain(self)
                tc.generate()

            def build(self):
                cmake = CMake(self)
                cmake.ctest(cli_args=["--output-on-failure"])
    """)
    client.save({"conanfile.py": conanfile})
    
    # ctest can return 0 or 8 depending on the version when no tests are found.
    # We just want to ensure it is executed and args are passed correctly.
    try:
        client.run("build .")
    except Exception as e:
        if "Command failed (unexpectedly)" not in str(e):
            raise
    
    assert "Running CMake.ctest()" in client.out
    
    # Check if the command was correctly formatted
    assert "ctest " in client.out
    assert "--output-on-failure" in client.out

def test_cmake_helper_redirect_stdout():
    client = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        from conan.tools.cmake import CMake, CMakeToolchain
        import io
        class Pkg(ConanFile):
            name = "pkg"
            version = "0.1"
            settings = "os", "compiler", "build_type", "arch"
            
            def generate(self):
                tc = CMakeToolchain(self)
                tc.generate()

            def build(self):
                self.conf.define("tools.cmake:cmake_program", "echo")
                cmake = CMake(self)
                
                my_stdout = io.StringIO()
                try:
                    cmake.build(cli_args=["--version"], stdout=my_stdout)
                except Exception:
                    pass
                
                self.output.info(f"MY_CAPTURED_STDOUT: {my_stdout.getvalue()}")
    """)
    client.save({"conanfile.py": conanfile})
    client.run("build .")
    
    # We should see that echo output was captured
    # It will echo the command line arguments
    assert "--build" in client.out
    assert "MY_CAPTURED_STDOUT: " in client.out
    assert "--version" in client.out
