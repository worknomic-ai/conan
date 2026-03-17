import sys
from conans.client.profile_loader import _ProfileValueParser
from conans.model.profile import Profile

profile_text = """
[replace_requires]
zlib/*: myzlib/1.2.3

[replace_tool_requires]
cmake/*: mycmake/3.20.0

[platform_requires]
openssl/3.0.0

[platform_tool_requires]
ninja/1.10.2

[system_tools]
old_ninja/1.10.0
"""

try:
    p = _ProfileValueParser.get_profile(profile_text)
    print("replace_requires:", p.replace_requires)
    print("replace_tool_requires:", p.replace_tool_requires)
    print("platform_requires:", p.platform_requires)
    print("platform_tool_requires:", p.platform_tool_requires)
    print("system_tools:", p.system_tools)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(p.dumps())
print(p.serialize())
