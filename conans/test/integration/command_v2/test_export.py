import json
import textwrap
from conans.test.utils.tools import TestClient

def test_export_pkglist_format():
    client = TestClient()
    conanfile = textwrap.dedent("""
        from conan import ConanFile
        class TestConan(ConanFile):
            name = "hello"
            version = "1.2"
            user = "myuser"
            channel = "mychannel"
        """)
    client.save({"conanfile.py": conanfile})
    client.run("export . --format=pkglist")
    out = json.loads(client.stdout)
    assert "Local Cache" in out
    assert "hello/1.2@myuser/mychannel" in out["Local Cache"]
    revs = out["Local Cache"]["hello/1.2@myuser/mychannel"]["revisions"]
    assert len(revs) == 1
    rev = list(revs.keys())[0]
    assert "timestamp" in revs[rev]

def test_export_pkglist_format_multiple():
    # just in case testing the formatter directly with multiple refs
    from conan.cli.commands.export import pkglist_export
    from conan.api.model import RecipeReference
    import io
    import sys
    
    ref1 = RecipeReference.loads("hello/1.0#rev1")
    ref2 = RecipeReference.loads("bye/2.0#rev2")
    
    # redirect stdout to capture json
    captured = io.StringIO()
    sys.stdout = captured
    try:
        pkglist_export([ref1, ref2])
    finally:
        sys.stdout = sys.__stdout__
    
    import json
    out = json.loads(captured.getvalue())
    assert "hello/1.0" in out["Local Cache"]
    assert "bye/2.0" in out["Local Cache"]
