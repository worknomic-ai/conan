import os
import sqlite3

from conan.api.output import ConanOutput
from conans.test.utils.tools import TestClient
from conans.util.dates import timestamp_now

def test_lru_migration_custom_storage_path():
    client = TestClient()
    storage_path = os.path.join(client.current_folder, "custom_storage")
    os.makedirs(storage_path, exist_ok=True)
    
    # Remove the default DB created by TestClient
    default_db = os.path.join(client.cache_folder, 'p', 'cache.sqlite3')
    if os.path.exists(default_db):
        os.remove(default_db)
    
    # Set the custom storage path in global.conf
    client.save({"global.conf": f"core.cache:storage_path={storage_path}"}, path=client.cache_folder)
    
    # Create the db with recipes and packages table without lru
    db_filename = os.path.join(storage_path, 'cache.sqlite3')
    conn = sqlite3.connect(db_filename)
    conn.execute("CREATE TABLE recipes (reference, rrev, path, timestamp);")
    conn.execute("CREATE TABLE packages (reference, rrev, pkgid, prev, path, timestamp, build_id);")
    conn.close()

    # Create an old version marker
    client.save({"version.txt": "2.0.13\n"}, path=client.cache_folder)

    # Trigger migration by calling any conan command
    client.run("config list")

    # Check that lru was added to the custom DB
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(recipes);")
    columns = [col[1] for col in cursor.fetchall()]
    assert "lru" in columns

    cursor.execute("PRAGMA table_info(packages);")
    columns = [col[1] for col in cursor.fetchall()]
    assert "lru" in columns
    conn.close()

    # Ensure no default DB was created
    assert not os.path.exists(default_db)
