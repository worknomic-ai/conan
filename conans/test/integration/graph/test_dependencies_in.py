from conans.test.utils.tools import TestClient, GenConanfile

def test_dependencies_in_operator():
    client = TestClient()
    client.save({
        "dep/conanfile.py": GenConanfile("dep", "1.0"),
        "tool/conanfile.py": GenConanfile("tool", "1.0"),
        "tst/conanfile.py": GenConanfile("tst", "1.0"),
        "pkg/conanfile.py": """from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    def requirements(self):
        self.requires("dep/1.0")
    def build_requirements(self):
        self.tool_requires("tool/1.0")
        self.test_requires("tst/1.0")
    def generate(self):
        self.output.info(f"dep in deps: {'dep' in self.dependencies}")
        self.output.info(f"tool in deps: {'tool' in self.dependencies}")
        self.output.info(f"tool in build deps: {'tool' in self.dependencies.build}")
        self.output.info(f"tst in deps: {'tst' in self.dependencies}")
        self.output.info(f"tst in test deps: {'tst' in self.dependencies.test}")
        self.output.info(f"missing in deps: {'missing' in self.dependencies}")
        self.output.info(f"malformed in deps: {'malformed/ref/' in self.dependencies}")
        self.output.info(f"invalid in deps: {'invalid@/' in self.dependencies}")
        self.output.info(f"int in deps: {123 in self.dependencies}")
"""
    })
    client.run("create dep")
    client.run("create tool")
    client.run("create tst")
    client.run("create pkg")

    assert "dep in deps: True" in client.out
    assert "tool in deps: False" in client.out
    assert "tool in build deps: True" in client.out
    assert "tst in deps: True" in client.out
    assert "tst in test deps: True" in client.out
    assert "missing in deps: False" in client.out
    assert "malformed in deps: False" in client.out
    assert "invalid in deps: False" in client.out
    assert "int in deps: False" in client.out
