import sys
sys.path.insert(0, '/tmp/hivolve/75a98f1e-be7/member-9f0a2177-c08')
from conan.api.conan_api import ConanAPI
from conans.client.graph.graph_builder import DepsGraphBuilder
from conans.model.requires import Requirements, Requirement
from conans.model.recipe_ref import RecipeReference
from collections import OrderedDict

reqs = Requirements()
req1 = Requirement(RecipeReference.loads("pkg/1.0"))
reqs._requires[req1] = req1

req_items = list(reqs._requires.items())

# Mutate req1
req1.ref = RecipeReference.loads("new_pkg/1.0")

# safe rebuild as in current code
reqs._requires = OrderedDict(req_items)

print(reqs._requires.keys())

# Now try to lookup using a new Requirement object
req_lookup = Requirement(RecipeReference.loads("new_pkg/1.0"))
print("lookup new_pkg:", req_lookup in reqs._requires)
print("lookup pkg:", Requirement(RecipeReference.loads("pkg/1.0")) in reqs._requires)

