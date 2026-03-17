import json
import os
import shutil
import tarfile

from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

def test_cache_save_restore_cross_platform_normalization():
    c = TestClient()
    c.save({"conanfile.py": GenConanfile("pkg", "0.1")})
    c.run("create .")
    
    # Get package ID
    c.run("list pkg/0.1:* --format=json")
    data = json.loads(c.stdout)
    pkg_id = list(data["Local Cache"]["pkg/0.1"]["revisions"].values())[0]["packages"].keys()
    pkg_id = list(pkg_id)[0]
    
    # Create an executable file in the package to test mode preservation
    c.run(f"cache path pkg/0.1:{pkg_id}")
    pkg_folder = str(c.stdout).strip()
    exec_file = os.path.join(pkg_folder, "my_tool.sh")
    with open(exec_file, "w") as f:
        f.write("#!/bin/bash\necho 'hello'")
    os.chmod(exec_file, 0o755)
    
    c.run("cache save pkg/*:* ")
    cache_path = os.path.join(c.current_folder, "conan_cache_save.tgz")
    assert os.path.exists(cache_path)
    
    # Inspect the generated tar file to ensure backslashes were converted and permissions normalized
    with tarfile.open(cache_path, "r:gz") as tar:
        for member in tar.getmembers():
            assert "\\" not in member.name  # Paths should be normalized to /
            assert member.uid == 0
            assert member.gid == 0
            assert member.uname == "root"
            assert member.gname == "root"
            
            # Directory should be 755
            if member.isdir():
                assert member.mode == 0o755
            # Regular files should have 644 or 755
            elif member.isfile():
                if member.name.endswith("my_tool.sh"):
                    assert member.mode == 0o755, f"{member.name} mode is {oct(member.mode)}"
                else:
                    assert member.mode in (0o644, 0o755)
                    
    # Now restore it
    c2 = TestClient()
    shutil.copy2(cache_path, c2.current_folder)
    c2.run("cache restore conan_cache_save.tgz")
    c2.run("list *:*#*")
    assert "pkg/0.1" in c2.out
    
    # Verify the executable bit is still there after restore
    c2.run(f"cache path pkg/0.1:{pkg_id}")
    restored_pkg_folder = str(c2.stdout).strip()
    restored_exec_file = os.path.join(restored_pkg_folder, "my_tool.sh")
    assert os.path.exists(restored_exec_file)
    # Check if executable
    assert os.stat(restored_exec_file).st_mode & 0o111
