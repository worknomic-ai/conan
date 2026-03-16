import os
import textwrap

from conans.test.utils.tools import TestClient
from conans.model.recipe_ref import RecipeReference

def test_export_pkg_metadata():
    c = TestClient(default_server_user=True)
    conanfile = textwrap.dedent("""
        import os
        from conan import ConanFile
        from conan.tools.files import save

        class Pkg(ConanFile):
            name = "pkg"
            version = "0.1"

            def build(self):
                save(self, os.path.join(self.package_metadata_folder, "logs", "mylogs.txt"), "some logs!!!")
                
            def package(self):
                save(self, os.path.join(self.package_metadata_folder, "logs", "pkg_logs.txt"), "pkg logs!!!")
    """)
    c.save({"conanfile.py": conanfile})
    c.run("build .")
    c.run("export-pkg .")
    
    ref = RecipeReference.loads("pkg/0.1")
    pref = c.get_latest_package_reference(ref)
    pref_layout = c.get_latest_pkg_layout(pref)
    
    assert os.path.exists(pref_layout.metadata())
    assert set(os.listdir(pref_layout.metadata())) == {"logs"}
    assert set(os.listdir(os.path.join(pref_layout.metadata(), "logs"))) == {"mylogs.txt", "pkg_logs.txt"}
