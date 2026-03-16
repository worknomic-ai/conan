import json
import os

from conans.test.utils.tools import TestClient

def test_cmakepresets_architecture_and_environment():
    client = TestClient()
    conanfile = """
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain

class MyPkg(ConanFile):
    name = "mypkg"
    version = "1.0"
    settings = "os", "compiler", "build_type", "arch"
    
    def generate(self):
        self.buildenv.append("MY_BUILD_VAR", "my_build_value")
        self.runenv.append("MY_RUN_VAR", "my_run_value")
        tc = CMakeToolchain(self)
        tc.generate()
"""
    client.save({"conanfile.py": conanfile})
    client.run("install . -s arch=armv8 -s os=Linux -s compiler=gcc -s compiler.version=11 -s build_type=Release")
    
    preset_path = os.path.join(client.current_folder, "CMakePresets.json")
    assert os.path.exists(preset_path)
    
    data = json.loads(client.load("CMakePresets.json"))
    
    # Check configurePresets
    conf = data["configurePresets"][0]
    assert conf["architecture"]["value"] == "ARM64"
    assert conf["environment"]["MY_BUILD_VAR"] == "$env{MY_BUILD_VAR} my_build_value"
    
    # Check testPresets
    test = data["testPresets"][0]
    assert test["environment"]["MY_RUN_VAR"] == "$env{MY_RUN_VAR} my_run_value"

def test_cmakepresets_without_arch_or_env():
    client = TestClient()
    conanfile = """
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain

class MyPkg(ConanFile):
    settings = "os", "compiler", "build_type"
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
"""
    client.save({"conanfile.py": conanfile})
    client.run("install . -s os=Linux -s compiler=gcc -s compiler.version=11 -s build_type=Release")
    
    preset_path = os.path.join(client.current_folder, "CMakePresets.json")
    data = json.loads(client.load("CMakePresets.json"))
    
    conf = data["configurePresets"][0]
    assert "architecture" not in conf
    assert "environment" not in conf
    
    test = data["testPresets"][0]
    assert "environment" not in test
