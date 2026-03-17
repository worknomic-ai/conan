from conans.model.recipe_ref import RecipeReference
from conans.model.requires import Requirement
ref = RecipeReference.loads("pkg/<host_version:pkg_name>")
print(ref)
print(ref.version)
print(ref.name)
print(type(ref.version))
