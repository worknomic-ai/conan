import sys
import json
from conans.client.profile_loader import _ProfileValueParser
from conans.model.profile import Profile

profile_text = """
[tool_requires]
cmake/*: mycmake/3.20.0
"""

p = _ProfileValueParser.get_profile(profile_text)
result = {"host": p.serialize()}
try:
    print(json.dumps(result))
except Exception as e:
    import traceback
    traceback.print_exc()
