import pytest
from conan.tools.cmake import CMake
from conan.tools.cmake.presets import write_cmake_presets
from conans.client.conf import get_default_settings_yml
from conans.model.conf import Conf
from conans.model.settings import Settings
from conans.test.utils.mocks import ConanFileMock
from conans.test.utils.test_files import temp_folder


def _setup_conanfile(generator, settings_dict=None):
    settings = Settings.loads(get_default_settings_yml())
    if settings_dict:
        for k, v in settings_dict.items():
            if k == "os":
                settings.os = v
            elif k == "build_type":
                settings.build_type = v
            elif k == "compiler":
                settings.compiler = v
    
    conanfile = ConanFileMock()
    conanfile.conf = Conf()
    conanfile.folders.generators = "."
    conanfile.folders.set_base_generators(temp_folder())
    conanfile.settings = settings
    
    write_cmake_presets(conanfile, "toolchain", generator, {})
    return conanfile


def test_ctest_single_config():
    conanfile = _setup_conanfile("Unix Makefiles", {"os": "Linux", "build_type": "Release"})
    cmake = CMake(conanfile)
    cmake.ctest()
    assert "ctest" in conanfile.command
    assert "--build-config" not in conanfile.command


def test_ctest_multi_config():
    conanfile = _setup_conanfile("Visual Studio 17 2022", {"os": "Windows", "build_type": "Debug"})
    cmake = CMake(conanfile)
    cmake.ctest()
    assert "ctest --build-config Debug" in conanfile.command


def test_ctest_custom_program():
    conanfile = _setup_conanfile("Unix Makefiles", {"os": "Linux", "build_type": "Release"})
    conanfile.conf.define("tools.cmake:ctest_program", "my_program")
    cmake = CMake(conanfile)
    cmake.ctest()
    assert "my_program" in conanfile.command
    assert "ctest" not in conanfile.command


def test_ctest_cli_args():
    conanfile = _setup_conanfile("Unix Makefiles", {"os": "Linux", "build_type": "Release"})
    cmake = CMake(conanfile)
    cmake.ctest(cli_args=["--verbose", "-R", "mytest"])
    assert "ctest --verbose -R mytest" in conanfile.command


def test_ctest_build_type_override():
    conanfile = _setup_conanfile("Visual Studio 17 2022", {"os": "Windows", "build_type": "Debug"})
    cmake = CMake(conanfile)
    cmake.ctest(build_type="Release")
    assert "ctest --build-config Release" in conanfile.command


def test_ctest_skip_test():
    conanfile = _setup_conanfile("Unix Makefiles", {"os": "Linux", "build_type": "Release"})
    conanfile.conf.define("tools.build:skip_test", True)
    cmake = CMake(conanfile)
    cmake.ctest()
    assert conanfile.command is None


def test_ctest_env_verification():
    conanfile = _setup_conanfile("Unix Makefiles", {"os": "Linux", "build_type": "Release"})

    envs = []

    def runner(*args, **kwargs):
        envs.append(kwargs.get("env"))
        return 0

    conanfile.runner = runner
    cmake = CMake(conanfile)

    cmake.ctest()
    assert envs[-1] == ["conanbuild", "conanrun"]

    cmake.ctest(env="myenv")
    assert envs[-1] == "myenv"
