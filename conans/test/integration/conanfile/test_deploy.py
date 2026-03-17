import os
from conans.test.utils.tools import TestClient, GenConanfile

def test_recipe_deploy_method_relative():
    """
    Test validates that a recipe with a custom deploy() method executes correctly
    and copies targeted files.
    """
    client = TestClient()
    client.save({"conanfile.py": GenConanfile("pkg", "0.1").with_package_file("file.txt", "content")})
    client.run("create .")

    conanfile = """
from conan import ConanFile
from conan.tools.files import copy
import os

class Pkg(ConanFile):
    requires = "pkg/0.1"

    def deploy(self):
        # Baseline relative path deployment
        copy(self, "*", src=self.dependencies["pkg"].package_folder, dst=os.path.join(self.deploy_folder, "my_relative_deploy"))
"""
    client.save({"conanfile.py": conanfile}, clean_first=True)
    client.run("install . --output-folder=output")
    
    assert "conanfile.py: Calling deploy()" in client.out
    # It should copy to output/my_relative_deploy because deploy_folder defaults to base_build which is output_folder
    assert os.path.exists(os.path.join(client.current_folder, "output", "my_relative_deploy", "file.txt"))

def test_recipe_deploy_method_absolute_path():
    """
    Test explicitly asserts that deploying to an absolute path preserves the exact path.
    """
    client = TestClient()
    client.save({"conanfile.py": GenConanfile("pkg", "0.1").with_package_file("file.txt", "content")})
    client.run("create .")

    abs_deploy_dir = os.path.join(client.current_folder, "my_absolute_deploy")

    conanfile = f"""
from conan import ConanFile
from conan.tools.files import copy
import os

class Pkg(ConanFile):
    requires = "pkg/0.1"

    def deploy(self):
        # Deploy to absolute path
        copy(self, "*", src=self.dependencies["pkg"].package_folder, dst="{abs_deploy_dir.replace(chr(92), '/')}")
"""
    client.save({"conanfile.py": conanfile}, clean_first=True)
    client.run("install .")
    
    assert "conanfile.py: Calling deploy()" in client.out
    assert os.path.exists(os.path.join(abs_deploy_dir, "file.txt"))

def test_full_deployer_absolute_path():
    """
    Test explicitly asserts that deploying to an absolute path preserves the exact path
    when using standard deployers.
    """
    client = TestClient()
    client.save({"conanfile.py": GenConanfile("pkg", "0.1").with_package_file("file.txt", "content")})
    client.run("create .")

    abs_deploy_dir = os.path.join(client.current_folder, "my_absolute_deploy")

    client.save({"conanfile.txt": "[requires]\npkg/0.1"}, clean_first=True)
    client.run(f"install . --deployer=full_deploy --deployer-folder='{abs_deploy_dir}'")

    assert os.path.exists(os.path.join(abs_deploy_dir, "full_deploy", "host", "pkg", "0.1", "file.txt"))

def test_full_deployer_relative_path():
    """
    Test explicitly asserts that deploying to a relative path correctly resolves relative
    to the base output folder (baseline assertion).
    """
    client = TestClient()
    client.save({"conanfile.py": GenConanfile("pkg", "0.1").with_package_file("file.txt", "content")})
    client.run("create .")

    client.save({"conanfile.txt": "[requires]\npkg/0.1"}, clean_first=True)
    client.run("install . --deployer=full_deploy --output-folder=output_folder")

    assert os.path.exists(os.path.join(client.current_folder, "output_folder", "full_deploy", "host", "pkg", "0.1", "file.txt"))

