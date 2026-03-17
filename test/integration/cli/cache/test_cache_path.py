import os
import pytest

from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

def test_cache_path_folder_exists_and_missing():
    client = TestClient()
    client.save({"conanfile.py": GenConanfile("pkg", "0.1")})
    client.run("create .")
    
    # Baseline behavior: existing folder
    # metadata folder should not exist initially unless generated, 
    # but source folder might exist? Let's use export_source or export.
    # The default folder without --folder is 'exports' for recipes.
    client.run("cache path pkg/0.1")
    assert "pkg" in client.out
    
    # We need to make sure a specific folder exists.
    # export_source folder is only created if there are exports_sources
    # Let's add export_source
    client.save({"conanfile.py": GenConanfile("pkg", "0.1").with_exports_sources("*"), "src.txt": "hello"})
    client.run("create .")
    
    client.run("cache path pkg/0.1 --folder export_source")
    assert "pkg" in client.out
    
    # Let's manually remove the source folder to simulate it missing
    client.run("cache path pkg/0.1 --folder source")
    source_path = client.out.strip()
    import shutil, os
    if os.path.exists(source_path):
        shutil.rmtree(source_path)
    
    client.run("cache path pkg/0.1 --folder source", assert_error=True)
    assert "'source' folder does not exist for the reference pkg/0.1" in client.out

    # Let's test with a package reference
    client.run("list pkg/0.1:* --format=json")
    import json
    data = json.loads(str(client.stdout))
    revs = data["Local Cache"]["pkg/0.1"]["revisions"]
    latest_rev = list(revs.keys())[0]
    pref = list(revs[latest_rev]["packages"].keys())[0]
    
    client.run(f"cache path pkg/0.1:{pref} --folder build")
    build_path = client.out.strip()
    assert "pkg" in client.out
    
    # clean build
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    client.run(f"cache path pkg/0.1:{pref} --folder build", assert_error=True)
    assert f"'build' folder does not exist for the reference pkg/0.1:{pref}" in client.out
