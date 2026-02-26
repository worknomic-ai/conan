from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
class Consumer(ConanFile):
    requires = "pkg/0.1"
    def validate(self):
        if self.settings.os == "Windows":
             raise ConanInvalidConfiguration("Windows not supported")
