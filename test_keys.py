from conans.client.graph.graph_builder import DepsGraphBuilder
from conans.model.requires import Requirements, Requirement
from conans.model.recipe_ref import RecipeReference

reqs = Requirements()
reqs("pkg/1.0")

print(reqs._requires)
for k, v in reqs._requires.items():
    print(type(k), type(v))

