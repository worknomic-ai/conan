import sys
import json
from conans.client.profile_loader import _ProfileValueParser
from conans.model.profile import Profile

profile_text = """
[replace_requires]
zlib/*: myzlib/1.2.3
"""

p = _ProfileValueParser.get_profile(profile_text)
result = {"host": p.serialize()}
try:
    print(json.dumps(result))
except Exception as e:
    import traceback
    traceback.print_exc()
