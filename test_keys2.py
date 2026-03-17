from conans.model.requires import Requirements, Requirement
from conans.model.recipe_ref import RecipeReference

reqs = Requirements()
reqs("pkg/1.0")

for k, v in reqs._requires.items():
    print("key type:", type(k), "val type:", type(v))

