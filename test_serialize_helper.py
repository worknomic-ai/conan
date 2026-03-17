from collections import OrderedDict
from conans.model.recipe_ref import RecipeReference

def to_serializable(v):
    if hasattr(v, "serialize"):
        return v.serialize()
    if hasattr(v, "dumps"):
        return v.dumps()
    if isinstance(v, dict):
        return {k: to_serializable(val) for k, val in v.items()}
    if isinstance(v, list):
        return [to_serializable(val) for val in v]
    if hasattr(v, "name") and hasattr(v, "version") and not isinstance(v, str): # cheap duck typing for ref
        return repr(v)
    return v

print(to_serializable({"a": [RecipeReference.loads("pkg/1.0")]}))
