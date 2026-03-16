import sys
import os
sys.path.append(os.getcwd())
from conans.client.profile_loader import _ProfileValueParser

profile_text = """
[replace_requires]
*: zlib/1.3
pkg/*: zlib/1.2

[replace_tool_requires]
*: cmake/3.20

[platform_requires]
*: myplatform/1.0

[platform_tool_requires]
*: myplatform_tool/1.0
"""
p = _ProfileValueParser.get_profile(profile_text)
print("Success:", p)
