import os
import textwrap
import platform
import pytest
from conans.test.utils.tools import TestClient

@pytest.mark.tool("cmake")
def test_cmake_ctest():
    """
    Test CMake.ctest() with a real CMake if available.
    """
    client = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        from conan.tools.cmake import CMake, CMakeToolchain
        from conan.tools.env import VirtualBuildEnv, VirtualRunEnv

        class App(ConanFile):
            settings = "os", "arch", "compiler", "build_type"
            exports_sources = "CMakeLists.txt", "test_app.cpp"

            def generate(self):
                tc = CMakeToolchain(self)
                tc.generate()
                
                self.buildenv_info.define("MY_BUILD_VAR", "MY_BUILD_VALUE")
                self.runenv_info.define("MY_RUN_VAR", "MY_RUN_VALUE")
                
                build_env = VirtualBuildEnv(self)
                build_env.generate()
                run_env = VirtualRunEnv(self)
                run_env.generate()

            def build(self):
                cmake = CMake(self)
                cmake.configure()
                cmake.build()
                cmake.ctest(cli_args=["-V"])
    """)
    
    cmakelists = textwrap.dedent("""
        cmake_minimum_required(VERSION 3.15)
        project(App CXX)
        enable_testing()
        add_executable(test_app test_app.cpp)
        add_test(NAME mytest COMMAND test_app)
    """)
    
    test_app = textwrap.dedent("""
        #include <cstdlib>
        #include <iostream>
        #include <string>
        int main() {
            const char* build_var = std::getenv("MY_BUILD_VAR");
            const char* run_var = std::getenv("MY_RUN_VAR");
            if (build_var && std::string(build_var) == "MY_BUILD_VALUE" &&
                run_var && std::string(run_var) == "MY_RUN_VALUE") {
                std::cout << "Environment variables found!" << std::endl;
                return 0;
            }
            std::cout << "Environment variables NOT found!" << std::endl;
            if (build_var) std::cout << "MY_BUILD_VAR=" << build_var << std::endl;
            else std::cout << "MY_BUILD_VAR NOT SET" << std::endl;
            if (run_var) std::cout << "MY_RUN_VAR=" << run_var << std::endl;
            else std::cout << "MY_RUN_VAR NOT SET" << std::endl;
            return 1;
        }
    """)
    
    client.save({"conanfile.py": conanfile,
                 "CMakeLists.txt": cmakelists,
                 "test_app.cpp": test_app})
    
    client.run("build . -s build_type=Release")
    assert "Running CMake.ctest()" in client.out
    assert "1/1 Test #1: mytest" in client.out
    assert "Passed" in client.out
    assert "Environment variables found!" in client.out


def test_cmake_ctest_mocked():
    """
    Functional test of CMake.ctest() using a mocked ctest program to verify 
    that it is called correctly and environment variables are passed.
    """
    client = TestClient(path_with_spaces=False)
    
    # Create fake ctest
    if platform.system() == "Windows":
        client.save({"my_ctest.bat": "@echo off\necho mock ctest\necho MY_BUILD_VAR=%MY_BUILD_VAR%"})
        ctest_program = os.path.join(client.current_folder, "my_ctest.bat").replace("\\", "/")
    else:
        client.save({"my_ctest": "#!/bin/sh\necho mock ctest\necho MY_BUILD_VAR=$MY_BUILD_VAR"})
        os.chmod(os.path.join(client.current_folder, "my_ctest"), 0o755)
        ctest_program = os.path.join(client.current_folder, "my_ctest")

    conanfile = textwrap.dedent("""
        from conan import ConanFile
        from conan.tools.cmake import CMake
        from conan.tools.env import Environment

        class App(ConanFile):
            settings = "os", "arch", "compiler", "build_type"

            def generate(self):
                from conan.tools.cmake.presets import write_cmake_presets
                write_cmake_presets(self, "toolchain", "Unix Makefiles", {})
                
                env = Environment()
                env.define("MY_BUILD_VAR", "MY_BUILD_VALUE")
                # Save as conanbuild so it's picked up by CMake.ctest() default env
                env.vars(self, scope="conanbuild").save_script("conanbuild")

            def build(self):
                cmake = CMake(self)
                cmake.ctest()
    """)
    
    client.save({"conanfile.py": conanfile})
    
    client.run(f'build . -s os=Linux -s arch=x86_64 -s compiler=gcc -s compiler.version=11 -s compiler.libcxx=libstdc++11 -s build_type=Release -c "tools.cmake:ctest_program={ctest_program}"')
    
    assert "Running CMake.ctest()" in client.out
    assert "mock ctest" in client.out
    
    # Verify the script was generated
    ext = "bat" if platform.system() == "Windows" else "sh"
    assert os.path.exists(os.path.join(client.current_folder, f"conanbuild.{ext}"))


def test_cmake_ctest_skip_test():
    client = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        from conan.tools.cmake import CMake
        class App(ConanFile):
            settings = "os", "arch", "compiler", "build_type"
            def build(self):
                cmake = CMake(self)
                cmake.ctest()
    """)
    client.save({"conanfile.py": conanfile})
    client.save({"CMakePresets.json": textwrap.dedent("""
        {
            "version": 3,
            "configurePresets": [
                {
                    "name": "default",
                    "generator": "Unix Makefiles",
                    "cacheVariables": {}
                }
            ]
        }
    """)})
    
    client.run("build . -s build_type=Release -c tools.build:skip_test=True")
    assert "Running CMake.ctest()" not in client.out
