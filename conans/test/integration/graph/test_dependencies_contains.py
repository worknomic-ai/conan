import textwrap
from conans.test.utils.tools import TestClient
from conans.test.assets.genconanfile import GenConanfile

def test_dependencies_contains():
    client = TestClient()
    client.save({"conanfile.py": GenConanfile()})
    client.run("create . --name=dep --version=0.1")
    client.run("create . --name=tool --version=0.1")
    client.run("create . --name=test_dep --version=0.1")

    conanfile = textwrap.dedent("""
        from conan import ConanFile
        from conans.model.recipe_ref import RecipeReference
        class Pkg(ConanFile):
            requires = "dep/0.1"
            tool_requires = "tool/0.1"
            test_requires = "test_dep/0.1"

            def generate(self):
                # Name checks
                # self.dependencies defaults to build=False, but doesn't filter by 'test' or 'direct'
                self.output.info(f"DEP IN DEPS: {'dep' in self.dependencies}")
                self.output.info(f"TOOL IN DEPS: {'tool' in self.dependencies}")
                self.output.info(f"TEST_DEP IN DEPS: {'test_dep' in self.dependencies}")
                self.output.info(f"MISSING IN DEPS: {'missing' in self.dependencies}")

                # Context checks
                self.output.info(f"DEP IN HOST: {'dep' in self.dependencies.host}")
                self.output.info(f"DEP IN BUILD: {'dep' in self.dependencies.build}")
                self.output.info(f"TOOL IN HOST: {'tool' in self.dependencies.host}")
                self.output.info(f"TOOL IN BUILD: {'tool' in self.dependencies.build}")
                self.output.info(f"TEST_DEP IN HOST: {'test_dep' in self.dependencies.host}")
                self.output.info(f"TEST_DEP IN TEST: {'test_dep' in self.dependencies.test}")

                # RecipeReference checks
                ref = RecipeReference.loads("dep/0.1")
                self.output.info(f"REF IN DEPS: {ref in self.dependencies}")
                ref_tool = RecipeReference.loads("tool/0.1")
                self.output.info(f"REF_TOOL IN DEPS: {ref_tool in self.dependencies}")
                self.output.info(f"REF_TOOL IN BUILD: {ref_tool in self.dependencies.build}")
                ref_test = RecipeReference.loads("test_dep/0.1")
                self.output.info(f"REF_TEST IN DEPS: {ref_test in self.dependencies}")
                self.output.info(f"REF_TEST IN TEST: {ref_test in self.dependencies.test}")
        """)
    client.save({"conanfile.py": conanfile})
    client.run("install . -pr:b=default")

    assert "conanfile.py: DEP IN DEPS: True" in client.out
    assert "conanfile.py: TOOL IN DEPS: False" in client.out
    assert "conanfile.py: TEST_DEP IN DEPS: True" in client.out
    assert "conanfile.py: MISSING IN DEPS: False" in client.out

    assert "conanfile.py: DEP IN HOST: True" in client.out
    assert "conanfile.py: DEP IN BUILD: False" in client.out
    assert "conanfile.py: TOOL IN HOST: False" in client.out
    assert "conanfile.py: TOOL IN BUILD: True" in client.out
    assert "conanfile.py: TEST_DEP IN HOST: False" in client.out
    assert "conanfile.py: TEST_DEP IN TEST: True" in client.out

    assert "conanfile.py: REF IN DEPS: True" in client.out
    assert "conanfile.py: REF_TOOL IN DEPS: False" in client.out
    assert "conanfile.py: REF_TOOL IN BUILD: True" in client.out
    assert "conanfile.py: REF_TEST IN DEPS: True" in client.out
    assert "conanfile.py: REF_TEST IN TEST: True" in client.out

def test_dependencies_contains_transitive():
    client = TestClient()
    client.save({"conanfile.py": GenConanfile()})
    client.run("create . --name=transitive --version=0.1")
    client.save({"conanfile.py": GenConanfile().with_requires("transitive/0.1")})
    client.run("create . --name=direct --version=0.1")

    conanfile = textwrap.dedent("""
        from conan import ConanFile
        class Pkg(ConanFile):
            requires = "direct/0.1"

            def generate(self):
                self.output.info(f"DIRECT IN DEPS: {'direct' in self.dependencies}")
                self.output.info(f"TRANSITIVE IN DEPS: {'transitive' in self.dependencies}")
        """)
    client.save({"conanfile.py": conanfile})
    client.run("install .")

    assert "conanfile.py: DIRECT IN DEPS: True" in client.out
    assert "conanfile.py: TRANSITIVE IN DEPS: True" in client.out
