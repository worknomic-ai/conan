import platform
import re
import textwrap

import pytest

from conans.test.utils.tools import TestClient
 
 
@pytest.mark.skipif(platform.system() != "Windows", reason="Only for windows")
def test_nmakedeps():
    client = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        class Pkg(ConanFile):
            settings = "os", "arch", "compiler", "build_type"
            name = "test-nmakedeps"
            version = "1.0"

            def package_info(self):
                self.cpp_info.components["pkg-1"].libs = ["pkg-1"]
                self.cpp_info.components["pkg-1"].defines = ["TEST_DEFINITION1"]
                self.cpp_info.components["pkg-1"].system_libs = ["ws2_32"]
                self.cpp_info.components["pkg-2"].libs = ["pkg-2"]
                self.cpp_info.components["pkg-2"].defines = ["TEST_DEFINITION2=0"]
                self.cpp_info.components["pkg-2"].requires = ["pkg-1"]
                self.cpp_info.components["pkg-3"].libs = ["pkg-3"]
                self.cpp_info.components["pkg-3"].defines = ["TEST_DEFINITION3="]
                self.cpp_info.components["pkg-3"].requires = ["pkg-1", "pkg-2"]
                self.cpp_info.components["pkg-4"].libs = ["pkg-4"]
                self.cpp_info.components["pkg-4"].defines = ["TEST_DEFINITION4=foo"]
                self.cpp_info.components["pkg-5"].libs = ["pkg-5"]
                self.cpp_info.components["pkg-5"].defines = ["TEST_DEFINITION5=foo bar"]
                self.cpp_info.components["pkg-6"].libs = ["pkg-6"]
                self.cpp_info.components["pkg-6"].defines = ["TEST_DEFINITION6=foo#bar"]
                self.cpp_info.components["pkg-7"].libs = ["pkg-7"]
                self.cpp_info.components["pkg-7"].defines = ["TEST_DEFINITION7=foo=bar"]
    """)
    client.save({"conanfile.py": conanfile})
    client.run("create . -s arch=x86_64")
    client.run("install --requires=test-nmakedeps/1.0"
               " -g NMakeDeps -s build_type=Release -s arch=x86_64")
    # Checking that NMakeDeps builds correctly .bat file
    bat_file = client.load("conannmakedeps.bat")
    # Checking that defines are added to CL
    for flag in (
        r"/DTEST_DEFINITION1", r"/DTEST_DEFINITION2#0",
        r"/DTEST_DEFINITION3#", r"/DTEST_DEFINITION4#foo",
        r'"/DTEST_DEFINITION5#foo bar"', r"/DTEST_DEFINITION6#foo#bar",
        r"/DTEST_DEFINITION7#foo#bar",
    ):
        assert re.search(fr'set "CL=%CL%.*\s{flag}(?:\s|")', bat_file)
    # Checking that libs and system libs are added to _LINK_
    for flag in (r"pkg-1\.lib", r"pkg-2\.lib", r"pkg-3\.lib", r"pkg-4\.lib",
                 r"pkg-5\.lib", r"pkg-6\.lib", r"pkg-7\.lib", r"ws2_32\.lib"):
        assert re.search(fr'set "_LINK_=%_LINK_%.*\s{flag}(?:\s|")', bat_file)


@pytest.mark.skipif(platform.system() != "Windows", reason="Only for windows")
def test_nmakedeps_defines_quoting():
    client = TestClient()
    conanfile = textwrap.dedent('''
        from conan import ConanFile
        class Pkg(ConanFile):
            name = "test-nmakedeps-quoting"
            version = "1.0"
            settings = "os", "arch", "compiler", "build_type"

            def package_info(self):
                self.cpp_info.defines = [
                    "WITHOUT_SPACE=NO_SPACE",
                    "WITH_SPACE=VALUE WITH SPACES",
                    "MULTIPLE_EQUALS=VALUE=WITH=EQUALS"
                ]
    ''')
    client.save({"conanfile.py": conanfile})
    client.run("create . -s arch=x86_64")
    
    client.run("install --requires=test-nmakedeps-quoting/1.0 -g NMakeDeps -s build_type=Release -s arch=x86_64")
    bat_file = client.load("conannmakedeps.bat")
    
    for flag in (r"/DWITHOUT_SPACE#NO_SPACE", 
                 r'"/DWITH_SPACE#VALUE WITH SPACES"',
                 r"/DMULTIPLE_EQUALS#VALUE#WITH#EQUALS"):
        assert re.search(fr'set "CL=%CL%.*\s{flag}(?:\s|")', bat_file)
