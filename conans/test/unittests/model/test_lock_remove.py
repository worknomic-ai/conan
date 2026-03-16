import os
import json
from conans.model.graph_lock import Lockfile
from conan.cli.commands.lock import lock_remove
from conans.model.recipe_ref import RecipeReference

def test_lock_remove_dict_mutation():
    lockfile = Lockfile()
    lockfile.add(requires=[RecipeReference.loads("pkg/1.0"), RecipeReference.loads("pkg2/1.0")],
                 build_requires=[RecipeReference.loads("tool/1.0")],
                 python_requires=[RecipeReference.loads("pytool/1.0")])
    
    lockfile.remove(requires=["pkg/*"], build_requires=["tool/*"], python_requires=["pytool/*"])
    
    # check mutation was safe and elements were removed
    assert len(lockfile._requires._requires) == 1
    assert "pkg2/1.0" in [str(r) for r in lockfile._requires._requires.keys()]
    assert len(lockfile._build_requires._requires) == 0
    assert len(lockfile._python_requires._requires) == 0

def test_lock_remove_invalid_pattern():
    lockfile = Lockfile()
    lockfile.add(requires=[RecipeReference.loads("pkg/1.0")])
    lockfile.remove(requires=["not_matching/*"])
    assert len(lockfile._requires._requires) == 1

