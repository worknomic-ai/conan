from conan import ConanFile
class Test(ConanFile):
    name = "test"
    version = "0.1"
    def source(self):
        self.output.debug("MY DEBUG MESSAGE")
        self.output.status("MY STATUS MESSAGE")
