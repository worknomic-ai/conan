class MockConanfile:
    class Settings:
        def get_safe(self, name): return "Windows"
    settings = Settings()
    settings_build = Settings()
    conf = {}

from conan.tools.env import Environment
env = Environment()
env.append("CL", "-I\"C:\\My Path\"")
print(env.vars(MockConanfile()).dumps())
