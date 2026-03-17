import os
from conan.tools.env import Environment
from conans.test.utils.mocks import ConanFileMock
from conan.internal.model.settings import Settings

class MockConanfile(object):
    def __init__(self):
        self.settings = Settings({"os": ["Windows", "Linux"]})
        self.settings.os = "Windows"
        self.settings_build = self.settings

c = MockConanfile()
env = Environment()
env.append("CL", '/DTEST#"Hello World"')
print(env.vars(c).script_contents("build"))