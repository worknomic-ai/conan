import json
import textwrap
import unittest
from collections import OrderedDict

from conan.tools.env.environment import ProfileEnvironment
from conans.model.profile import Profile
from conans.model.recipe_ref import RecipeReference


class ProfileTest(unittest.TestCase):

    def test_profile_settings_update(self):
        new_profile = Profile()
        new_profile.update_settings(OrderedDict([("os", "Windows")]))

        new_profile.update_settings(OrderedDict([("OTHER", "2")]))
        self.assertEqual(new_profile.settings, OrderedDict([("os", "Windows"), ("OTHER", "2")]))

        new_profile.update_settings(OrderedDict([("compiler", "2"), ("compiler.version", "3")]))
        self.assertEqual(new_profile.settings,
                         OrderedDict([("os", "Windows"), ("OTHER", "2"),
                                      ("compiler", "2"), ("compiler.version", "3")]))

    def test_profile_subsettings_update(self):
        new_profile = Profile()
        new_profile.update_settings(OrderedDict([("os", "Windows"),
                                                ("compiler", "Visual Studio"),
                                                ("compiler.runtime", "MT")]))

        new_profile.update_settings(OrderedDict([("compiler", "gcc")]))
        self.assertEqual(dict(new_profile.settings), {"compiler": "gcc", "os": "Windows"})

        new_profile = Profile()
        new_profile.update_settings(OrderedDict([("os", "Windows"),
                                                 ("compiler", "Visual Studio"),
                                                 ("compiler.runtime", "MT")]))

        new_profile.update_settings(OrderedDict([("compiler", "Visual Studio"),
                                                 ("compiler.subsetting", "3"),
                                                 ("other", "value")]))

        self.assertEqual(dict(new_profile.settings), {"compiler": "Visual Studio",
                                                      "os": "Windows",
                                                      "compiler.runtime": "MT",
                                                      "compiler.subsetting": "3",
                                                      "other": "value"})

    def test_package_settings_update(self):
        np = Profile()
        np.update_package_settings({"MyPackage": [("os", "Windows")]})

        np.update_package_settings({"MyPackage": [("OTHER", "2")]})
        self.assertEqual(np.package_settings_values,
                         {"MyPackage": [("os", "Windows"), ("OTHER", "2")]})

        np._package_settings_values = None  # invalidate caching
        np.update_package_settings({"MyPackage": [("compiler", "2"), ("compiler.version", "3")]})
        self.assertEqual(np.package_settings_values,
                         {"MyPackage": [("os", "Windows"), ("OTHER", "2"),
                                        ("compiler", "2"), ("compiler.version", "3")]})

    def test_profile_dump_order(self):
        # Settings
        profile = Profile()
        profile.package_settings["zlib"] = {"compiler": "gcc"}
        profile.settings["arch"] = "x86_64"
        profile.settings["compiler"] = "Visual Studio"
        profile.settings["compiler.version"] = "12"
        profile.tool_requires["*"] = ["zlib/1.2.8@lasote/testing"]
        profile.tool_requires["zlib/*"] = ["aaaa/1.2.3@lasote/testing",
                                                 "bb/1.2@lasote/testing"]
        self.assertEqual("""[settings]
arch=x86_64
compiler=Visual Studio
compiler.version=12
zlib:compiler=gcc
[tool_requires]
*: zlib/1.2.8@lasote/testing
zlib/*: aaaa/1.2.3@lasote/testing, bb/1.2@lasote/testing
""".splitlines(), profile.dumps().splitlines())

    def test_apply(self):
        # Settings
        profile = Profile()
        profile.settings["arch"] = "x86_64"
        profile.settings["compiler"] = "Visual Studio"
        profile.settings["compiler.version"] = "12"

        profile.update_settings(OrderedDict([("compiler.version", "14")]))

        self.assertEqual('[settings]\narch=x86_64\ncompiler=Visual Studio'
                         '\ncompiler.version=14\n',
                         profile.dumps())


def test_update_build_requires():
    # https://github.com/conan-io/conan/issues/8205#issuecomment-775032229
    profile = Profile()
    profile.tool_requires["*"] = ["zlib/1.2.8"]

    profile2 = Profile()
    profile2.tool_requires["*"] = ["zlib/1.2.8"]

    profile.compose_profile(profile2)
    assert profile.tool_requires["*"] == ["zlib/1.2.8"]

    profile3 = Profile()
    profile3.tool_requires["*"] = ["zlib/1.2.11"]

    profile.compose_profile(profile3)
    assert profile.tool_requires["*"] == ["zlib/1.2.11"]

    profile4 = Profile()
    profile4.tool_requires["*"] = ["cmake/2.7"]

    profile.compose_profile(profile4)
    assert profile.tool_requires["*"] == ["zlib/1.2.11", "cmake/2.7"]


def test_profile_serialize():
    profile = Profile()
    profile.options.update(options_values={"zlib*:aoption": "1", "zlib*:otheroption": "1"})
    profile.buildenv = ProfileEnvironment.loads("VAR1=1\nVAR2=2")
    profile.runenv = ProfileEnvironment.loads("VAR3=3\nVAR4=4")
    profile.system_tools = ["tool/1.0", "another/2.0"]
    profile.replace_requires = {RecipeReference.loads("pkg/1.0"): RecipeReference.loads("pkg/2.0")}
    profile.platform_requires = {"pkg2/1.0": "pkg2/1.0"}
    profile.conf.update("user.myfield:value", "MyVal")
    profile.settings["arch"] = "x86_64"
    profile.settings["compiler"] = "Visual Studio"
    profile.settings["compiler.version"] = "12"
    profile.tool_requires["*"] = ["zlib/1.2.8"]
    profile.update_package_settings({"MyPackage": [("os", "Windows")]})

    serialized = profile.serialize()
    assert serialized["settings"] == {"arch": "x86_64", "compiler": "Visual Studio", "compiler.version": "12"}
    assert serialized["package_settings"] == {"MyPackage": {"os": "Windows"}}
    assert serialized["options"] == {"zlib*:aoption": "1", "zlib*:otheroption": "1"}
    assert serialized["tool_requires"] == {"*": ["zlib/1.2.8"]}
    assert serialized["system_tools"] == ["tool/1.0", "another/2.0"]
    assert serialized["replace_requires"] == {"pkg/1.0": "pkg/2.0"}
    assert serialized["platform_requires"] == {"pkg2/1.0": "pkg2/1.0"}
    assert serialized["conf"] == {"user.myfield:value": "MyVal"}
    assert serialized["build_env"] == "VAR1=1\nVAR2=2\n"
    assert serialized["run_env"] == "VAR3=3\nVAR4=4\n"

