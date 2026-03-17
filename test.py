from conans.test.utils.tools import TestClient, GenConanfile
client = TestClient()
client.save({"conanfile.py": GenConanfile("dep1", "1.0")})
client.run("create .")
client.save({"conanfile.py": GenConanfile("dep2", "1.0").with_require("dep1/1.0")})
client.run("create .")

consumer = """
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

class Consumer(ConanFile):
    name = "consumer"
    version = "1.0"
    settings = "os", "compiler", "build_type", "arch"
    requires = "dep2/1.0"
    generators = "CMakeToolchain", "CMakeDeps"

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
"""
cmakelists = """
cmake_minimum_required(VERSION 3.15)
project(consumer)

include(${CMAKE_BINARY_DIR}/conandeps.cmake)

add_executable(main main.cpp)
target_link_libraries(main dep2::dep2)
"""

main = "int main() { return 0; }"

client.save({"conanfile.py": consumer, "CMakeLists.txt": cmakelists, "main.cpp": main}, clean_first=True)
client.run("build .")
