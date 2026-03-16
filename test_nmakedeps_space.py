from conan.tools.env import Environment
class MockConanfile:
    class Settings:
        def get_safe(self, name): return "Windows"
    settings = Settings()
    settings_build = Settings()
    conf = {}
    win_bash = False
    win_bash_run = False
    generators_folder = "."
    folders = type('Folders', (), {'source': '', 'build': '', 'generators': ''})()

env = Environment()
env.append("CL", "/DFOO#\\\"bar baz\\\"")
v = env.vars(MockConanfile())
f = "conannmakedeps.bat"
v.save_script(f)
with open(f) as file:
    print(file.read())
