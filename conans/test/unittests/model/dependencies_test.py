import pytest
from conans.model.dependencies import UserRequirementsDict
from conans.model.recipe_ref import RecipeReference

class MockRequire:
    def __init__(self, ref, build=False):
        self.ref = ref
        self.build = build
    def __repr__(self):
        return f"MockRequire({self.ref}, build={self.build})"

def test_user_requirements_dict_contains_ambiguous():
    ref1 = RecipeReference.loads("pkg/1.0")
    ref2 = RecipeReference.loads("pkg/2.0")
    req1 = MockRequire(ref1, build=False)
    req2 = MockRequire(ref2, build=False)
    
    data = {req1: "value1", req2: "value2"}
    urd = UserRequirementsDict(data)
    
    # "pkg" matches both req1 and req2 because they have the same name and build=False
    # This is an ambiguous match.
    assert "pkg" in urd

def test_user_requirements_dict_contains():
    ref1 = RecipeReference.loads("pkg/1.0")
    req1 = MockRequire(ref1, build=False)
    
    data = {req1: "value1"}
    urd = UserRequirementsDict(data)
    
    assert "pkg" in urd
    assert "pkg/1.0" in urd
    assert ref1 in urd
    assert "other" not in urd
    assert 123 not in urd
