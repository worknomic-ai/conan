import sys
sys.path.insert(0, '/tmp/hivolve/75a98f1e-be7/member-9f0a2177-c08')
from conan.api.conan_api import ConanAPI
from conans.model.requires import Requirements, Requirement
from conans.model.recipe_ref import RecipeReference
from collections import OrderedDict

reqs = Requirements()
req1 = Requirement(RecipeReference.loads("pkg/1.0"))
reqs._requires[req1.ref.name] = req1

print("Is key a string?", list(reqs._requires.keys())[0] == "pkg")
