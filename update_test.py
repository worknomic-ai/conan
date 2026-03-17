import re
with open("conans/test/integration/graph/test_profile_overrides.py", "r") as f:
    content = f.read()

new_test = """
def test_replace_requires_transitive_lookup():
    # Test that a transitive dependency replaced by a profile override can be
    # correctly looked up by its new name in the consumer's generate() or build() method.
    client = TestClient()
    conanfile_pkg = \"\"\"from conan import ConanFile
class Pkg(ConanFile):
    name = "pkg"
    version = "1.0"
    requires = "dep/1.0"
    def generate(self):
        # We replaced 'transitive' with 'mydep', so we should be able to look it up
        assert "mydep" in self.dependencies
        assert self.dependencies["mydep"].ref.name == "mydep"
        # The original name should not be present
        assert "transitive" not in self.dependencies
\"\"\"
    client.save({
        "mydep/conanfile.py": GenConanfile("mydep", "1.0"),
        "dep/conanfile.py": GenConanfile("dep", "1.0").with_require("transitive/1.0"),
        "pkg/conanfile.py": conanfile_pkg,
        "profile": "[replace_requires]\\ntransitive/*: mydep/1.0"
    })
    client.run("create mydep")
    client.run("export dep")
    client.run("create pkg -pr profile --build=missing")
    assert "mydep/1.0" in client.out
"""

# Replace the current implementation with GenConanfile where appropriate
content = re.sub(r'\n+def test_replace_requires_transitive_lookup\(\):.*', '\n' + new_test, content, flags=re.DOTALL)

with open("conans/test/integration/graph/test_profile_overrides.py", "w") as f:
    f.write(content)
