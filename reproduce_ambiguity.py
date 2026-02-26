from collections import OrderedDict
from conans.model.dependencies import UserRequirementsDict
from conans.model.recipe_ref import RecipeReference

class MockRequire:
    def __init__(self, name, build=False):
        self.ref = RecipeReference.loads(f"{name}/1.0")
        self.build = build
    def __getattr__(self, name):
        return False

def test_ambiguity():
    req1 = MockRequire("pkg", build=False)
    req2 = MockRequire("pkg", build=False) # Same name and same context!
    
    data = OrderedDict([
        (req1, "value1"),
        (req2, "value2")
    ])
    
    deps = UserRequirementsDict(data)
    
    print(f"Contains 'pkg': {'pkg' in deps}")
    try:
        print(f"Get 'pkg': {deps.get('pkg')}")
    except Exception as e:
        print(f"Get 'pkg' error: {e}")

if __name__ == "__main__":
    test_ambiguity()
