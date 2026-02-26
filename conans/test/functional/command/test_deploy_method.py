import os
import textwrap
from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

class TestDeployMethod:
    def test_deploy_method_called(self):
        c = TestClient()
        conanfile = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                def deploy(self):
                    self.output.info("DEPLOY CALLED!!!")
        """)
        c.save({"conanfile.py": conanfile})
        c.run("install .")
        assert "DEPLOY CALLED!!!" in c.out

    def test_deploy_method_access_dependencies(self):
        c = TestClient()
        c.save({"dep/conanfile.py": GenConanfile("dep", "1.0")})
        c.run("create dep")

        conanfile = textwrap.dedent("""
            from conan import ConanFile
            import os
            class Pkg(ConanFile):
                requires = "dep/1.0"
                def deploy(self):
                    dep = self.dependencies["dep"]
                    self.output.info(f"DEP NAME: {dep.ref.name}")
                    self.output.info(f"DEP FOLDER: {os.path.exists(dep.package_folder)}")
        """)
        c.save({"conanfile.py": conanfile})
        c.run("install .")
        assert "DEP NAME: dep" in c.out
        assert "DEP FOLDER: True" in c.out

    def test_deploy_method_copy_files(self):
        c = TestClient()
        c.save({"dep/conanfile.py": GenConanfile("dep", "1.0").with_package_file("bin/hello.exe", "content")})
        c.run("create dep")

        conanfile = textwrap.dedent("""
            from conan import ConanFile
            from conan.tools.files import copy
            import os
            class Pkg(ConanFile):
                requires = "dep/1.0"
                def deploy(self):
                    dep = self.dependencies["dep"]
                    # Copying to the folder where conan install is called
                    copy(self, "hello.exe", os.path.join(dep.package_folder, "bin"), self.generators_folder)
        """)
        c.save({"conanfile.py": conanfile})
        c.run("install .")
        assert os.path.exists(os.path.join(c.current_folder, "hello.exe"))
        assert "content" == c.load("hello.exe")

    def test_deploy_method_no_deploy_defined(self):
        c = TestClient()
        c.save({"conanfile.py": GenConanfile()})
        c.run("install .")
        assert "Error in deploy() method" not in c.out

    def test_deploy_method_exception_formatted(self):
        c = TestClient()
        conanfile = textwrap.dedent("""
            from conan import ConanFile
            from conans.errors import ConanException
            class Pkg(ConanFile):
                def deploy(self):
                    raise ConanException("KABOOM!")
        """)
        c.save({"conanfile.py": conanfile})
        c.run("install .", assert_error=True)
        assert "conanfile.py: Error in deploy() method, line 6" in c.out
        assert "ConanException: KABOOM!" in c.out

    def test_deploy_method_dependencies_contains(self):
        c = TestClient()
        c.save({"dep/conanfile.py": GenConanfile("dep", "1.0")})
        c.run("create dep")

        conanfile = textwrap.dedent("""
            from conan import ConanFile
            class Pkg(ConanFile):
                requires = "dep/1.0"
                def deploy(self):
                    if "dep" in self.dependencies:
                        self.output.info("DEP IN DEPENDENCIES")
        """)
        c.save({"conanfile.py": conanfile})
        c.run("install .")
        assert "DEP IN DEPENDENCIES" in c.out
