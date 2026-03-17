import json
import os
import textwrap

from conans.test.utils.tools import TestClient


def test_profile_path():
    c = TestClient()
    c.run("profile path default")
    assert "default" in c.out


def test_profile_path_missing():
    c = TestClient()
    c.run("profile path notexisting", assert_error=True)
    assert "ERROR: Profile not found: notexisting" in c.out


def test_ignore_paths_when_listing_profiles():
    c = TestClient()
    ignore_path = '.DS_Store'

    # just in case
    os.makedirs(c.cache.profiles_path, exist_ok=True)
    # This a "touch" equivalent
    open(os.path.join(c.cache.profiles_path, '.DS_Store'), 'w').close()
    os.utime(os.path.join(c.cache.profiles_path, ".DS_Store"))

    c.run("profile list")

    assert ignore_path not in c.out


def test_shorthand_syntax():
    tc = TestClient()
    tc.save({"profile": "[conf]\nuser:profile=True"})
    tc.run("profile show -h")
    assert "[-pr:b" in tc.out
    assert "[-pr:h" in tc.out
    assert "[-pr:a" in tc.out

    tc.run(
        "profile show -o:a=both_options=True -pr:a=profile -s:a=os=WindowsCE -s:a=os.platform=conan -c:a=user.conf:cli=True -f=json")

    out = json.loads(tc.out)
    assert out == {'host': {'settings': {'os': 'WindowsCE', 'os.platform': 'conan'}, 'package_settings': {}, 'options': {'both_options': 'True'}, 'tool_requires': {}, 'system_tools': [], 'conf': {'user.conf:cli': True, 'user:profile': True}, 'build_env': '', 'runenv': '', 'processed_settings': {'os': 'WindowsCE', 'os.platform': 'conan'}}, 'build': {'settings': {'os': 'WindowsCE', 'os.platform': 'conan'}, 'package_settings': {}, 'options': {'both_options': 'True'}, 'tool_requires': {}, 'system_tools': [], 'conf': {'user.conf:cli': True, 'user:profile': True}, 'build_env': '', 'runenv': '', 'processed_settings': {'os': 'WindowsCE', 'os.platform': 'conan'}}}

    tc.save({"pre": textwrap.dedent("""
            [settings]
            os=Linux
            compiler=gcc
            compiler.version=11
            """),
             "mid": textwrap.dedent("""
            [settings]
            compiler=clang
            compiler.version=14
            """),
             "post": textwrap.dedent("""
            [settings]
            compiler.version=13
            """)})

    tc.run("profile show -pr:a=pre -pr:a=mid -pr:a=post -f=json")
    out = json.loads(tc.out)
    assert out == {'host': {'settings': {'os': 'Linux', 'compiler': 'clang', 'compiler.version': '13'}, 'package_settings': {}, 'options': {}, 'tool_requires': {}, 'system_tools': [], 'conf': {}, 'build_env': '', 'runenv': '', 'processed_settings': {'os': 'Linux', 'compiler': 'clang', 'compiler.version': '13'}}, 'build': {'settings': {'os': 'Linux', 'compiler': 'clang', 'compiler.version': '13'}, 'package_settings': {}, 'options': {}, 'tool_requires': {}, 'system_tools': [], 'conf': {}, 'build_env': '', 'runenv': '', 'processed_settings': {'os': 'Linux', 'compiler': 'clang', 'compiler.version': '13'}}}

    tc.run("profile show -pr:a=pre -pr:h=post -f=json")
    out = json.loads(tc.out)
    assert out == {'host': {'settings': {'os': 'Linux', 'compiler': 'gcc', 'compiler.version': '13'}, 'package_settings': {}, 'options': {}, 'tool_requires': {}, 'system_tools': [], 'conf': {}, 'build_env': '', 'runenv': '', 'processed_settings': {'os': 'Linux', 'compiler': 'gcc', 'compiler.version': '13'}}, 'build': {'settings': {'os': 'Linux', 'compiler': 'gcc', 'compiler.version': '11'}, 'package_settings': {}, 'options': {}, 'tool_requires': {}, 'system_tools': [], 'conf': {}, 'build_env': '', 'runenv': '', 'processed_settings': {'os': 'Linux', 'compiler': 'gcc', 'compiler.version': '11'}}}

    tc.run("profile show -pr:a=pre -o:b foo=False -o:a foo=True -o:h foo=False -f=json")
    out = json.loads(tc.out)
    assert out == {'host': {'settings': {'os': 'Linux', 'compiler': 'gcc', 'compiler.version': '11'}, 'package_settings': {}, 'options': {'foo': 'False'}, 'tool_requires': {}, 'system_tools': [], 'conf': {}, 'build_env': '', 'runenv': '', 'processed_settings': {'os': 'Linux', 'compiler': 'gcc', 'compiler.version': '11'}}, 'build': {'settings': {'os': 'Linux', 'compiler': 'gcc', 'compiler.version': '11'}, 'package_settings': {}, 'options': {'foo': 'True'}, 'tool_requires': {}, 'system_tools': [], 'conf': {}, 'build_env': '', 'runenv': '', 'processed_settings': {'os': 'Linux', 'compiler': 'gcc', 'compiler.version': '11'}}}


def test_profile_show_json():
    c = TestClient()
    c.save({"myprofilewin": "[settings]\nos=Windows",
            "myprofilelinux": "[settings]\nos=Linux"})
    c.run("profile show -pr:b=myprofilewin -pr:h=myprofilelinux --format=json")
    profile = json.loads(c.stdout)
    assert profile["build"]["settings"] == {"os": "Windows"}
    assert profile["host"]["settings"] == {"os": "Linux"}


def test_profile_show_json_tool_requires():
    c = TestClient()
    c.save({"myprofile": textwrap.dedent("""\
        [settings]
        os=Windows
        [tool_requires]
        mytool/1.0
        [system_tools]
        sys_tool/1.0
        """)})

    c.save({"profile.py": textwrap.dedent("""\
        from conans.model.recipe_ref import RecipeReference
        def profile_plugin(profile):
            profile.tool_requires.setdefault("*", []).append(RecipeReference.loads("dynamic_tool/2.0"))
            profile.replace_requires = {RecipeReference.loads("zlib/1.2.8"): RecipeReference.loads("zlib/1.2.9")}
        """)}, path=c.cache.plugins_path)

    c.run("profile show -pr myprofile --format=json")
    
    # Assert the stdout stream receives only JSON, isolated from informational stderr logs.
    assert "host" in c.stdout
    assert "build" in c.stdout
    assert c.stderr == ""
    
    profile = json.loads(c.stdout)
    
    # Assert JSON structural validity and correct stream routing
    assert profile["host"]["settings"] == {"os": "Windows"}
    
    # Assert tool_requires is formatted correctly (e.g. as list of strings)
    assert profile["host"]["tool_requires"] == {"*": ["mytool/1.0", "dynamic_tool/2.0"]}
    assert profile["host"]["system_tools"] == ["sys_tool/1.0"]
    assert profile["host"]["replace_requires"] == {"zlib/1.2.8": "zlib/1.2.9"}
