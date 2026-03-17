import platform
import textwrap

import pytest

from conans.test.utils.tools import TestClient

@pytest.mark.skipif(platform.system() != "Windows", reason="Only for windows")
@pytest.mark.tool("visual_studio")
def test_nmakedeps_quoting():
    client = TestClient()
    dep_conanfile = textwrap.dedent("""
        from conan import ConanFile

        class Dep(ConanFile):
            name = "dep"
            version = "1.0"

            def package_info(self):
                self.cpp_info.defines.append('MY_MACRO="Hello World"')
        """)

    consumer_conanfile = textwrap.dedent("""
        from conan import ConanFile

        class Consumer(ConanFile):
            name = "consumer"
            version = "1.0"
            settings = "os", "compiler", "build_type", "arch"
            requires = "dep/1.0"
            generators = "NMakeDeps", "NMakeToolchain"

            def build(self):
                self.run("nmake /f makefile")
        """)

    makefile = textwrap.dedent("""\
        !if exist(conan_toolchain.mak)
        !include conan_toolchain.mak
        !endif

        all: main.exe

        main.exe: main.cpp
        \tcl.exe main.cpp $(conan_cxxflags) /Fe$@
        """)

    main_cpp = textwrap.dedent("""\
        #include <iostream>

        #define STR(x) #x
        #define STRINGIFY(x) STR(x)

        int main() {
            std::cout << "Macro value: " << STRINGIFY(MY_MACRO) << "\\n";
            return 0;
        }
        """)

    client.save({
        "dep/conanfile.py": dep_conanfile,
        "consumer/conanfile.py": consumer_conanfile,
        "consumer/makefile": makefile,
        "consumer/main.cpp": main_cpp,
    })

    client.run("create dep")
    
    settings = "-s compiler=msvc -s compiler.version=190 -s compiler.cppstd=14 -s compiler.runtime=dynamic"
    client.run(f"build consumer {settings}")
    
    client.run_command("consumer\\\\main.exe")
    assert 'Macro value: "Hello World"' in client.out
