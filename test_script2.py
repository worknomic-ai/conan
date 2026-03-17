import json
from conan.tools.env.environment import ProfileEnvironment
from conans.model.profile import Profile
from conans.model.recipe_ref import RecipeReference

profile = Profile()
# Dynamically inject replace_requires
profile.replace_requires = {RecipeReference.loads("zlib/1.2.8"): RecipeReference.loads("zlib/1.2.9")}

try:
    print(json.dumps(profile.serialize(), indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()
