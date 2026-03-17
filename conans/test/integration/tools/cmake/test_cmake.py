import textwrap

from conans.test.utils.tools import TestClient

def test_ctest():
    client = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        from conan.tools.cmake import CMake

        class Pkg(ConanFile):
            name = "pkg"
            version = "0.1"
            settings = "os", "compiler", "build_type", "arch"
            generators = "CMakeToolchain"

            def build(self):
                cmake = CMake(self)
                cmake.ctest(cli_args=["--extra-args"])

            def run(self, command, *args, **kwargs):
                self.output.info(f"MYRUN: {command}")
    """)

    client.save({"conanfile.py": conanfile})
    client.run("create .")
    
    assert "MYRUN: ctest --extra-args" in client.out or "MYRUN: ctest --build-config Release --extra-args" in client.out


def test_ctest_complex_path():
    client = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        from conan.tools.cmake import CMake

        class Pkg(ConanFile):
            name = "pkg"
            version = "0.1"
            settings = "os", "compiler", "build_type", "arch"
            generators = "CMakeToolchain"

            def build(self):
                cmake = CMake(self)
                cmake.ctest(cli_args=["--extra-args"])

            def run(self, command, *args, **kwargs):
                self.output.info(f"MYRUN: {command}")
    """)

    client.save({
        "conanfile.py": conanfile
    })
    # Use an overlapping path that contains 'cmake' multiple times
    client.run("create . -c tools.cmake:cmake_program=/opt/cmake/bin/cmake")
    assert "/opt/cmake/bin/ctest" in client.out
    assert "/opt/ctest" not in client.out
