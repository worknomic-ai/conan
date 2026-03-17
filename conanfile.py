from conan import ConanFile

class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    settings = "os", "compiler"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    
    def package_id(self):
        pass
