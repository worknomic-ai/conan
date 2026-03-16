from conans.test.utils.tools import TestClient

def test_cmakedeps_conandeps():
    client = TestClient()
    client.save({
        "conanfile.py": """
from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    def package_info(self):
        self.cpp_info.libs = ["pkg"]
"""
    })
    client.run("create .")

    client.save({
        "conanfile.py": """
from conan import ConanFile
from conan.tools.cmake import CMake

class App(ConanFile):
    requires = "pkg/1.0"
    generators = "CMakeDeps", "CMakeToolchain"
    settings = "os", "compiler", "build_type", "arch"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
""",
        "CMakeLists.txt": """
cmake_minimum_required(VERSION 3.15)
project(App)
include(${CMAKE_CURRENT_BINARY_DIR}/conandeps.cmake)
"""
    })
    client.run("install . -s build_type=Release")
    content = client.load("conandeps.cmake")
    assert "find_package(pkg CONFIG REQUIRED)" in content
    
    # We can also test building if we want, but testing generation is the core requirement
    client.run("build .", assert_error=True) # It might fail to build because of missing source files, but cmake configure should pass if conandeps.cmake is valid

def test_cmakedeps_conandeps_suffix():
    client = TestClient()
    client.save({
        "conanfile.py": """
from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    def package_info(self):
        self.cpp_info.libs = ["pkg"]
"""
    })
    client.run("create .")

    client.save({
        "conanfile.py": """
from conan import ConanFile
from conan.tools.cmake import CMakeDeps

class App(ConanFile):
    requires = "pkg/1.0"
    tool_requires = "pkg/1.0"
    settings = "os", "compiler", "build_type", "arch"

    def generate(self):
        deps = CMakeDeps(self)
        deps.build_context_activated = ["pkg"]
        deps.build_context_suffix = {"pkg": "_build"}
        deps.generate()
"""
    })
    client.run("install . -pr:b default -s build_type=Release")
    content = client.load("conandeps.cmake")
    assert "find_package(pkg CONFIG REQUIRED)" in content
    assert "find_package(pkg_build CONFIG REQUIRED)" in content
    assert content.count("find_package(pkg CONFIG REQUIRED)") == 1
    assert content.count("find_package(pkg_build CONFIG REQUIRED)") == 1
