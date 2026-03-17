import sys
sys.path.insert(0, '/tmp/hivolve/75a98f1e-be7/member-9f0a2177-c08')
from conan.api.conan_api import ConanAPI
from conans.model.requires import Requirements, Requirement
from conans.model.recipe_ref import RecipeReference

reqs = Requirements()
reqs("pkg/1.0")
for k, v in reqs._requires.items():
    print("key type:", type(k), "val type:", type(v), "key:", k)

