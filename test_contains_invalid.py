from conans.model.dependencies import UserRequirementsDict
from conans.model.recipe_ref import RecipeReference
from collections import OrderedDict

def test_invalid_ref():
    data = OrderedDict()
    deps = UserRequirementsDict(data)
    try:
        print(f"Result for invalid: {'invalid/ref@#$' in deps}")
    except Exception as e:
        print(f"Caught exception: {type(e).__name__}: {e}")

test_invalid_ref()
