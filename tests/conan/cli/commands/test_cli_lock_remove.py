import json
import os
from conans.test.utils.tools import TestClient

def test_lock_remove_cli():
    client = TestClient()
    lock_dict = {
        "version": "0.5",
        "requires": [
            "pkg1/1.0",
            "pkg2/1.0#rev1"
        ],
        "build_requires": [
            "tool1/1.0"
        ]
    }
    client.save({"conan.lock": json.dumps(lock_dict)})
    
    client.run("lock remove --lockfile=conan.lock --requires=pkg1/* --build-requires=tool1/*")
    
    lock_content = client.load("conan.lock")
    lock_data = json.loads(lock_content)
    
    assert "pkg1/1.0" not in lock_data["requires"]
    assert "pkg2/1.0#rev1" in lock_data["requires"]
    assert "build_requires" not in lock_data or len(lock_data["build_requires"]) == 0

def test_lock_remove_cli_all():
    client = TestClient()
    lock_dict = {
        "version": "0.5",
        "requires": [
            "pkg1/1.0",
            "pkg2/1.0#rev1"
        ]
    }
    client.save({"conan.lock": json.dumps(lock_dict)})
    client.run("lock remove --lockfile=conan.lock --requires=*")
    
    lock_data = json.loads(client.load("conan.lock"))
    assert "requires" not in lock_data or len(lock_data["requires"]) == 0
