import json
import os

from conans.test.utils.tools import TestClient

def test_cmake_presets_architecture_and_env():
    client = TestClient()
    conanfile_tool = """
from conan import ConanFile
class Tool(ConanFile):
    name = "tool"
    version = "1.0"
    def package_info(self):
        self.buildenv_info.define("MY_BUILD_VAR", "mybuildvalue")
        self.buildenv_info.append_path("PATH", "mybuildpath")
"""
    conanfile_lib = """
from conan import ConanFile
class Lib(ConanFile):
    name = "lib"
    version = "1.0"
    def package_info(self):
        self.runenv_info.define("MY_RUN_VAR", "myrunvalue")
        self.runenv_info.append_path("PATH", "myrunpath")
"""
    client.save({"tool.py": conanfile_tool, "lib.py": conanfile_lib})
    client.run("create tool.py")
    client.run("create lib.py")

    conanfile = """
from conan import ConanFile

class Pkg(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain"
    tool_requires = "tool/1.0"
    requires = "lib/1.0"
"""
    client.save({"conanfile.py": conanfile})
    client.run('install . -s os=Windows -s compiler="msvc" -s compiler.version=190 -s compiler.runtime=dynamic -s arch=x86_64')
    
    presets_path = os.path.join(client.current_folder, "CMakePresets.json")
    assert os.path.exists(presets_path)
    data = json.loads(client.load("CMakePresets.json"))
    
    config_preset = data["configurePresets"][0]
    build_preset = data["buildPresets"][0]
    test_preset = data["testPresets"][0]

    assert config_preset["architecture"]["value"] == "x64"
    assert config_preset["architecture"]["strategy"] == "set"
    
    # Configure and build presets should have build environment
    assert config_preset["environment"]["MY_BUILD_VAR"] == "mybuildvalue"
    assert "mybuildpath" in config_preset["environment"]["PATH"]
    assert "$penv{PATH}" in config_preset["environment"]["PATH"]

    assert build_preset["environment"]["MY_BUILD_VAR"] == "mybuildvalue"
    assert "mybuildpath" in build_preset["environment"]["PATH"]
    assert "$penv{PATH}" in build_preset["environment"]["PATH"]
    
    # Test presets should have run environment
    assert test_preset["environment"]["MY_RUN_VAR"] == "myrunvalue"
    assert "myrunpath" in test_preset["environment"]["PATH"]
    assert "$penv{PATH}" in test_preset["environment"]["PATH"]



