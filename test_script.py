import json
from conan.tools.env.environment import ProfileEnvironment
from conans.model.profile import Profile

profile = Profile()
profile.options.loads("zlib*:aoption=1\nzlib*:otheroption=1")
profile.buildenv = ProfileEnvironment.loads("VAR1=1\nVAR2=2")
profile.conf.update("user.myfield:value", "MyVal")
profile.settings["arch"] = "x86_64"
profile.settings["compiler"] = "Visual Studio"
profile.settings["compiler.version"] = "12"
profile.tool_requires["*"] = ["zlib/1.2.8"]
profile.update_package_settings({"MyPackage": [("os", "Windows")]})

try:
    print(json.dumps(profile.serialize(), indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()
