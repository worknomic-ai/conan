import os
import platform
import textwrap

import pytest

from conans.test.utils.tools import TestClient

@pytest.mark.skipif(platform.system() not in ["Windows"], reason="Requires Windows")
def test_vcvars_winsdk_version_string():
    client = TestClient(path_with_spaces=False)

    conanfile = textwrap.dedent("""
        from conan import ConanFile
        class TestConan(ConanFile):
            generators = "VCVars"
            settings = "os", "compiler", "arch", "build_type"
    """)
    client.save({"conanfile.py": conanfile})
    client.run('install . -s os=Windows -s compiler="msvc" -s compiler.version=191 '
               '-s compiler.cppstd=14 -s compiler.runtime=static -s arch=x86_64 -c tools.microsoft:winsdk_version=10.0.19041.0')

    assert os.path.exists(os.path.join(client.current_folder, "conanvcvars.bat"))
    vcvars = client.load("conanvcvars.bat")
    assert "10.0.19041.0" in vcvars

@pytest.mark.skipif(platform.system() not in ["Windows"], reason="Requires Windows")
def test_vcvars_winsdk_version_integer():
    client = TestClient(path_with_spaces=False)

    conanfile = textwrap.dedent("""
        from conan import ConanFile
        class TestConan(ConanFile):
            generators = "VCVars"
            settings = "os", "compiler", "arch", "build_type"
    """)
    # Pass an integer-like version through profile/conf to test `check_type=str` enforcement
    client.save({
        "conanfile.py": conanfile,
        "profile": "[conf]\ntools.microsoft:winsdk_version=10\n"
    })
    client.run('install . -s os=Windows -s compiler="msvc" -s compiler.version=191 '
               '-s compiler.cppstd=14 -s compiler.runtime=static -s arch=x86_64 -pr profile')

    assert os.path.exists(os.path.join(client.current_folder, "conanvcvars.bat"))
    vcvars = client.load("conanvcvars.bat")
    assert " 10 " in vcvars or " 10" in vcvars
