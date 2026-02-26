import textwrap
from conans.test.utils.tools import TestClient

def test_warnings_as_errors_cli():
    client = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        class Pkg(ConanFile):
            def configure(self):
                self.output.warning("This is a deprecated warning", warn_tag="deprecated")
        """)
    client.save({"conanfile.py": conanfile})

    # Promoting to error via CLI
    client.run("graph info . -c core:warnings_as_errors=['deprecated']", assert_error=True)
    print(f"OUTPUT:\n{client.out}")
    assert "ConanException: deprecated: This is a deprecated warning" in client.out
    print("CLI propagation test passed!")

if __name__ == "__main__":
    test_warnings_as_errors_cli()
