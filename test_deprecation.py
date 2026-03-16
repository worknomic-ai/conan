import sys
import os
sys.path.append(os.getcwd())
from conans.model.profile import Profile
from conans.client.profile_loader import _ProfileValueParser
from conans.util.config_parser import ConfigParser

def test_load():
    profile_text = """
[system_tools]
myplatform_tool/1.0
"""
    try:
        p = _ProfileValueParser.get_profile(profile_text)
        print("Success:", p)
    except Exception as e:
        print("Failed:", e)

test_load()
