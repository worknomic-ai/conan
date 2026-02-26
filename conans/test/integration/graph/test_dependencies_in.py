import textwrap
from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

class TestDependenciesIn:
    def test_dependencies_in(self):
        c = TestClient()
        c.save({"dep/conanfile.py": GenConanfile("dep", "1.0"),
                "consumer/conanfile.py": textwrap.dedent("""
                    from conan import ConanFile
                    from conans.model.recipe_ref import RecipeReference
                    class Pkg(ConanFile):
                        name = "consumer"
                        version = "0.1"
                        requires = "dep/1.0"
                        def generate(self):
                            self.output.warning(f"DEP IN HOST: {'dep' in self.dependencies}")
                            self.output.warning(f"DEP REF IN HOST: {RecipeReference.loads('dep/1.0') in self.dependencies}")
                            self.output.warning(f"OTHER IN HOST: {'other' in self.dependencies}")
                    """)
                })
        c.run("create dep")
        c.run("install consumer")
        assert "DEP IN HOST: True" in c.out
        assert "DEP REF IN HOST: True" in c.out
        assert "OTHER IN HOST: False" in c.out

    def test_dependencies_in_contexts(self):
        c = TestClient()
        c.save({"dep_host/conanfile.py": GenConanfile("dep_host", "1.0"),
                "dep_build/conanfile.py": GenConanfile("dep_build", "1.0"),
                "consumer/conanfile.py": textwrap.dedent("""
                    from conan import ConanFile
                    class Pkg(ConanFile):
                        name = "consumer"
                        version = "0.1"
                        requires = "dep_host/1.0"
                        tool_requires = "dep_build/1.0"
                        def generate(self):
                            self.output.warning(f"HOST IN ALL: {'dep_host' in self.dependencies}")
                            # By default self.dependencies search in the host context
                            self.output.warning(f"BUILD IN ALL: {'dep_build' in self.dependencies}")
                            
                            self.output.warning(f"HOST IN HOST: {'dep_host' in self.dependencies.host}")
                            self.output.warning(f"BUILD IN HOST: {'dep_build' in self.dependencies.host}")
                            
                            self.output.warning(f"HOST IN BUILD: {'dep_host' in self.dependencies.build}")
                            self.output.warning(f"BUILD IN BUILD: {'dep_build' in self.dependencies.build}")
                    """)
                })
        c.run("create dep_host")
        c.run("create dep_build")
        c.run("install consumer")
        assert "HOST IN ALL: True" in c.out
        assert "BUILD IN ALL: False" in c.out
        assert "HOST IN HOST: True" in c.out
        assert "BUILD IN HOST: False" in c.out
        assert "HOST IN BUILD: False" in c.out
        assert "BUILD IN BUILD: True" in c.out

    def test_dependencies_in_test_requires(self):
        c = TestClient()
        c.save({"test_dep/conanfile.py": GenConanfile("test_dep", "1.0"),
                "consumer/conanfile.py": textwrap.dedent("""
                    from conan import ConanFile
                    class Pkg(ConanFile):
                        name = "consumer"
                        version = "0.1"
                        def build_requirements(self):
                            self.test_requires("test_dep/1.0")
                        def generate(self):
                            self.output.warning(f"TEST IN HOST: {'test_dep' in self.dependencies.host}")
                            self.output.warning(f"TEST IN TEST: {'test_dep' in self.dependencies.test}")
                    """)
                })
        c.run("create test_dep")
        c.run("install consumer")
        assert "TEST IN HOST: False" in c.out
        assert "TEST IN TEST: True" in c.out

    def test_dependencies_in_transitive(self):
        c = TestClient()
        c.save({"dep_a/conanfile.py": GenConanfile("dep_a", "1.0"),
                "dep_b/conanfile.py": GenConanfile("dep_b", "1.0").with_requires("dep_a/1.0"),
                "consumer/conanfile.py": textwrap.dedent("""
                    from conan import ConanFile
                    class Pkg(ConanFile):
                        name = "consumer"
                        version = "0.1"
                        requires = "dep_b/1.0"
                        def generate(self):
                            self.output.warning(f"DEP_B IN HOST: {'dep_b' in self.dependencies}")
                            self.output.warning(f"DEP_A IN HOST: {'dep_a' in self.dependencies}")
                    """)
                })
        c.run("create dep_a")
        c.run("create dep_b")
        c.run("install consumer")
        assert "DEP_B IN HOST: True" in c.out
        assert "DEP_A IN HOST: True" in c.out

    def test_dependencies_in_wrong_version(self):
        c = TestClient()
        c.save({"dep/conanfile.py": GenConanfile("dep", "1.0"),
                "consumer/conanfile.py": textwrap.dedent("""
                    from conan import ConanFile
                    from conans.model.recipe_ref import RecipeReference
                    class Pkg(ConanFile):
                        name = "consumer"
                        version = "0.1"
                        requires = "dep/1.0"
                        def generate(self):
                            self.output.warning(f"DEP 1.0 IN HOST: {RecipeReference.loads('dep/1.0') in self.dependencies}")
                            self.output.warning(f"DEP 2.0 IN HOST: {RecipeReference.loads('dep/2.0') in self.dependencies}")
                    """)
                })
        c.run("create dep")
        c.run("install consumer")
        assert "DEP 1.0 IN HOST: True" in c.out
        assert "DEP 2.0 IN HOST: False" in c.out
