import json
from conans.model.profile import Profile
from conans.model.recipe_ref import RecipeReference

p = Profile()
p.tool_requires["*"] = [RecipeReference.loads("cmake/3.20.0")]
try:
    print(json.dumps(p.serialize()))
except Exception as e:
    print("FAILED:", type(e), e)
