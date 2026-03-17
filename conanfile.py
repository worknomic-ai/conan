from conan import ConanFile

class Pkg(ConanFile):
    def set_name(self):
        self.name = "other_name"
    def set_version(self):
        self.version = "2.0"
