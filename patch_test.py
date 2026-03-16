import os

file_path = "conans/test/integration/toolchains/microsoft/test_nmakedeps.py"
with open(file_path, "r") as f:
    content = f.read()

# Add a test that covers spaces and =
new_test = """

@pytest.mark.skipif(platform.system() != "Windows", reason="Only for windows")
def test_nmakedeps_spaces_and_quotes():
    client = TestClient()
    conanfile = textwrap.dedent('''
        from conan import ConanFile
        class Pkg(ConanFile):
            settings = "os", "arch", "compiler", "build_type"
            name = "test-nmakedeps"
            version = "1.0"

            def package_info(self):
                self.cpp_info.components["pkg-1"].libs = ["pkg 1"]
                self.cpp_info.components["pkg-1"].defines = ["TEST_DEF=With Space"]
                self.cpp_info.components["pkg-1"].cflags = ["-I", "C:\\\\My Path"]
                self.cpp_info.components["pkg-1"].system_libs = ["ws2 32"]
                self.cpp_info.components["pkg-1"].sharedlinkflags = ["/OPT:VAR=1 2 3"]
    ''')
    client.save({"conanfile.py": conanfile})
    client.run("create . -s arch=x86_64")
    client.run("install --requires=test-nmakedeps/1.0"
               " -g NMakeDeps -s build_type=Release -s arch=x86_64")
    bat_file = client.load("conannmakedeps.bat")
    
    assert re.search(r'set "_LINK_=%_LINK_%.*\\s"pkg 1\\.lib"(?:\\s|")', bat_file)
    assert re.search(r'set "_LINK_=%_LINK_%.*\\s"ws2 32\\.lib"(?:\\s|")', bat_file)
    assert re.search(r'set "CL=%CL%.*\\s/DTEST_DEF#\\\\"With Space\\\\""(?:\\s|")', bat_file)
    assert re.search(r'set "CL=%CL%.*\\s"-I"(?:\\s|")', bat_file)
    assert re.search(r'set "CL=%CL%.*\\s"C:\\\\My Path"(?:\\s|")', bat_file)
    assert re.search(r'set "_LINK_=%_LINK_%.*\\s"/OPT:VAR=1 2 3"(?:\\s|")', bat_file)
"""

content += new_test
with open(file_path, "w") as f:
    f.write(content)
