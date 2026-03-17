import pytest
import sys
import io
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


def test_cmake_stream_capture():
    client = TestClient()

    mock_cmake = textwrap.dedent("""
        import sys
        print("MOCK_CMAKE_STDOUT: " + " ".join(sys.argv[1:]))
        sys.stderr.write("MOCK_CMAKE_STDERR: " + " ".join(sys.argv[1:]) + "\\n")
    """)
    client.save({"mock_cmake.py": mock_cmake})

    mock_cmake_path = client.current_folder + "/mock_cmake.py"
    mock_cmake_path = mock_cmake_path.replace("\\\\", "/")

    mock_ctest = textwrap.dedent("""
        import sys
        print("MOCK_CTEST_STDOUT: " + " ".join(sys.argv[1:]))
        sys.stderr.write("MOCK_CTEST_STDERR: " + " ".join(sys.argv[1:]) + "\\n")
    """)
    client.save({"mock_ctest.py": mock_ctest})

    mock_ctest_path = client.current_folder + "/mock_ctest.py"
    mock_ctest_path = mock_ctest_path.replace("\\\\", "/")

    # Get python executable path for the command
    python_exe = sys.executable.replace("\\\\", "/")

    conanfile = textwrap.dedent(f"""
        from conan import ConanFile
        from conan.tools.cmake import CMake
        import io
        import sys

        class Pkg(ConanFile):
            name = "pkg"
            version = "0.1"
            settings = "os", "compiler", "build_type", "arch"
            generators = "CMakeToolchain"

            def build(self):
                # configure cmake_program to our mock
                self.conf.define("tools.cmake:cmake_program", '"{python_exe}" "{mock_cmake_path}"')
                cmake = CMake(self)

                myout = io.StringIO()
                myerr = io.StringIO()
                cmake.configure(stdout=myout, stderr=myerr)
                assert "MOCK_CMAKE_STDOUT" in myout.getvalue()
                assert "MOCK_CMAKE_STDERR" in myerr.getvalue()

                myout = io.StringIO()
                myerr = io.StringIO()
                cmake.build(stdout=myout, stderr=myerr)
                assert "MOCK_CMAKE_STDOUT" in myout.getvalue()
                assert "MOCK_CMAKE_STDERR" in myerr.getvalue()

                myout = io.StringIO()
                myerr = io.StringIO()
                cmake.test(stdout=myout, stderr=myerr)
                assert "MOCK_CMAKE_STDOUT" in myout.getvalue()
                assert "MOCK_CMAKE_STDERR" in myerr.getvalue()

                myout = io.StringIO()
                myerr = io.StringIO()

                def custom_run(command, *args, **kwargs):
                    if command.startswith("ctest"):
                        command = command.replace("ctest", '"{python_exe}" "{mock_ctest_path}"')
                    super(Pkg, self).run(command, *args, **kwargs)
                self.run = custom_run

                cmake.ctest(stdout=myout, stderr=myerr)
                assert "MOCK_CTEST_STDOUT" in myout.getvalue()
                assert "MOCK_CTEST_STDERR" in myerr.getvalue()

                myout = io.StringIO()
                myerr = io.StringIO()
                cmake.install(stdout=myout, stderr=myerr)
                assert "MOCK_CMAKE_STDOUT" in myout.getvalue()
                assert "MOCK_CMAKE_STDERR" in myerr.getvalue()

    """)
    client.save({"conanfile.py": conanfile})

    client.run("create .")

    # Verify the output doesn't bleed into standard client out.
    assert "MOCK_CMAKE_STDOUT" not in client.out
    assert "MOCK_CMAKE_STDERR" not in client.out
    assert "MOCK_CTEST_STDOUT" not in client.out
    assert "MOCK_CTEST_STDERR" not in client.out
