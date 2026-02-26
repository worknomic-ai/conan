from conan import ConanFile
class Consumer(ConanFile):
    requires = "pkg/[>0.0]"
