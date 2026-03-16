import sys
import os
sys.path.append(os.getcwd())
import json
from conans.model.profile import Profile
from conans.model.recipe_ref import RecipeReference

p = Profile()
p.tool_requires["*"] = [RecipeReference.loads("zlib/1.3")]
try:
    print(json.dumps(p.serialize()))
except Exception as e:
    print("Failed:", e)
