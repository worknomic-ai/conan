import json
import os
import shutil
import tarfile
from io import BytesIO

from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient
from conans.util.files import save, load


def test_cache_save_restore():
    c = TestClient()
    c.save({"conanfile.py": GenConanfile().with_settings("os")})
    c.run("create . --name=pkg --version=1.0 -s os=Linux")
    c.run("create . --name=pkg --version=1.1 -s os=Linux")
    c.run("create . --name=other --version=2.0 -s os=Linux")
    c.run("cache save pkg/*:* ")
    cache_path = os.path.join(c.current_folder, "conan_cache_save.tgz")
    assert os.path.exists(cache_path)
    _validate_restore(cache_path)


def test_cache_save_downloaded_restore():
    """ what happens if we save packages downloaded from server, not
    created
    """
    c = TestClient(default_server_user=True)
    c.save({"conanfile.py": GenConanfile().with_settings("os")})
    c.run("create . --name=pkg --version=1.0 -s os=Linux")
    c.run("create . --name=pkg --version=1.1 -s os=Linux")
    c.run("create . --name=other --version=2.0 -s os=Linux")
    c.run("upload * -r=default -c")
    c.run("remove * -c")
    c.run("download *:* -r=default --metadata=*")
    c.run("cache save pkg/*:* ")
    cache_path = os.path.join(c.current_folder, "conan_cache_save.tgz")
    assert os.path.exists(cache_path)

    _validate_restore(cache_path)


def _validate_restore(cache_path):
    c2 = TestClient()
    # Create a package in the cache to check put doesn't interact badly
    c2.save({"conanfile.py": GenConanfile().with_settings("os")})
    c2.run("create . --name=pkg2 --version=3.0 -s os=Windows")
    shutil.copy2(cache_path, c2.current_folder)
    c2.run("cache restore conan_cache_save.tgz")
    c2.run("list *:*#*")
    assert "pkg2/3.0" in c2.out
    assert "pkg/1.0" in c2.out
    assert "pkg/1.1" in c2.out
    assert "other/2.0" not in c2.out

    # Restore again, just in case
    c2.run("cache restore conan_cache_save.tgz")
    c2.run("list *:*#*")
    assert "pkg2/3.0" in c2.out
    assert "pkg/1.0" in c2.out
    assert "pkg/1.1" in c2.out
    assert "other/2.0" not in c2.out


def test_cache_save_restore_metadata():
    c = TestClient()
    c.save({"conanfile.py": GenConanfile().with_settings("os")})
    c.run("create . --name=pkg --version=1.0 -s os=Linux")
    pid = c.created_package_id("pkg/1.0")
    # Add some metadata
    c.run("cache path pkg/1.0 --folder=metadata")
    metadata_path = str(c.stdout).strip()
    myfile = os.path.join(metadata_path, "logs", "mylogs.txt")
    save(myfile, "mylogs!!!!")
    c.run(f"cache path pkg/1.0:{pid} --folder=metadata")
    pkg_metadata_path = str(c.stdout).strip()
    myfile = os.path.join(pkg_metadata_path, "logs", "mybuildlogs.txt")
    save(myfile, "mybuildlogs!!!!")

    c.run("cache save  pkg/*:* ")
    cache_path = os.path.join(c.current_folder, "conan_cache_save.tgz")
    assert os.path.exists(cache_path)

    # restore and check
    c2 = TestClient()
    shutil.copy2(cache_path, c2.current_folder)
    c2.run("cache restore conan_cache_save.tgz")
    c2.run("cache path pkg/1.0 --folder=metadata")
    metadata_path = str(c2.stdout).strip()
    myfile = os.path.join(metadata_path, "logs", "mylogs.txt")
    assert load(myfile) == "mylogs!!!!"
    c2.run(f"cache path pkg/1.0:{pid} --folder=metadata")
    pkg_metadata_path = str(c2.stdout).strip()
    myfile = os.path.join(pkg_metadata_path, "logs", "mybuildlogs.txt")
    assert load(myfile) == "mybuildlogs!!!!"


def test_cache_save_restore_multiple_revisions():
    c = TestClient()
    c.save({"conanfile.py": GenConanfile("pkg", "0.1")})
    c.run("create .")
    rrev1 = c.exported_recipe_revision()
    c.save({"conanfile.py": GenConanfile("pkg", "0.1").with_class_attribute("var=42")})
    c.run("create .")
    rrev2 = c.exported_recipe_revision()
    c.save({"conanfile.py": GenConanfile("pkg", "0.1").with_class_attribute("var=123")})
    c.run("create .")
    rrev3 = c.exported_recipe_revision()

    def check_ordered_revisions(client):
        client.run("list *#* --format=json")
        revisions = json.loads(client.stdout)["Local Cache"]["pkg/0.1"]["revisions"]
        assert revisions[rrev1]["timestamp"] < revisions[rrev2]["timestamp"]
        assert revisions[rrev2]["timestamp"] < revisions[rrev3]["timestamp"]

    check_ordered_revisions(c)

    c.run("cache save pkg/*#*:* ")
    cache_path = os.path.join(c.current_folder, "conan_cache_save.tgz")

    # restore and check
    c2 = TestClient()
    shutil.copy2(cache_path, c2.current_folder)
    c2.run("cache restore conan_cache_save.tgz")
    check_ordered_revisions(c2)


def test_cache_save_restore_graph():
    """ It is possible to save package list
    """
    c = TestClient()
    c.save({"dep/conanfile.py": GenConanfile("dep", "0.1"),
            "pkg/conanfile.py": GenConanfile("pkg", "0.1").with_requires("dep/0.1")})
    c.run("create dep")
    c.run("create pkg --format=json", redirect_stdout="graph.json")
    c.run("list --graph=graph.json --format=json", redirect_stdout="list.json")
    c.run("cache save --file=cache.tgz --list=list.json")
    cache_path = os.path.join(c.current_folder, "cache.tgz")
    assert os.path.exists(cache_path)
    c2 = TestClient()
    # Create a package in the cache to check put doesn't interact badly
    c2.save({"conanfile.py": GenConanfile().with_settings("os")})
    c2.run("create . --name=pkg2 --version=3.0 -s os=Windows")
    shutil.copy2(cache_path, c2.current_folder)
    c2.run("cache restore cache.tgz")
    c2.run("list *:*#*")
    assert "pkg/0.1" in c2.out
    assert "dep/0.1" in c2.out


def test_cache_save_path_normalization():
    c = TestClient()
    c.save({"conanfile.py": GenConanfile()})
    c.run("create . --name=pkg --version=1.0")
    c.run("cache save pkg/1.0")
    cache_path = os.path.join(c.current_folder, "conan_cache_save.tgz")

    with tarfile.open(cache_path, "r:gz") as tar:
        for member in tar.getmembers():
            assert "\\" not in member.name
            if member.name == "pkglist.json":
                f = tar.extractfile(member)
                assert f is not None
                pkglist = json.loads(f.read().decode())
                # Check that folders in pkglist.json also use forward slashes
                for ref_data in pkglist.values():
                    for rev_data in ref_data.get("revisions", {}).values():
                        assert "\\" not in rev_data.get("recipe_folder", "")
                        for pref_data in rev_data.get("packages", {}).values():
                            assert "\\" not in pref_data.get("package_folder", "")
                            if "metadata_folder" in pref_data:
                                assert "\\" not in pref_data.get("metadata_folder", "")


def test_cache_restore_path_normalization():
    c = TestClient()
    c.save({"conanfile.py": GenConanfile()})
    c.run("create . --name=pkg --version=1.0")
    c.run("cache save pkg/1.0")
    cache_path = os.path.join(c.current_folder, "conan_cache_save.tgz")

    # Create a new archive with backslashes
    backslashed_cache_path = os.path.join(c.current_folder, "backslashed.tgz")
    with tarfile.open(cache_path, "r:gz") as src_tar:
        with tarfile.open(backslashed_cache_path, "w:gz") as dst_tar:
            for member in src_tar.getmembers():
                if member.name == "pkglist.json":
                    f = src_tar.extractfile(member)
                    assert f is not None
                    pkglist = json.loads(f.read().decode())
                    # Inject backslashes in pkglist
                    for ref_data in pkglist.values():
                        for rev_data in ref_data.get("revisions", {}).values():
                            if "recipe_folder" in rev_data:
                                rev_data["recipe_folder"] = rev_data["recipe_folder"].replace("/", "\\")
                            for pref_data in rev_data.get("packages", {}).values():
                                if "package_folder" in pref_data:
                                    pref_data["package_folder"] = pref_data["package_folder"].replace("/", "\\")
                                if "metadata_folder" in pref_data:
                                    pref_data["metadata_folder"] = pref_data["metadata_folder"].replace("/", "\\")

                    data = json.dumps(pkglist).encode("utf-8")
                    new_member = tarfile.TarInfo(name="pkglist.json")
                    new_member.size = len(data)
                    dst_tar.addfile(new_member, BytesIO(data))
                else:
                    # Inject backslashes in member name
                    if member.isfile():
                        f = src_tar.extractfile(member)
                        member.name = member.name.replace("/", "\\")
                        dst_tar.addfile(member, f)
                    else:
                        member.name = member.name.replace("/", "\\")
                        dst_tar.addfile(member)

    # Now try to restore
    c2 = TestClient()
    shutil.copy2(backslashed_cache_path, c2.current_folder)
    c2.run("cache restore backslashed.tgz")
    c2.run("list *:*#*")
    assert "pkg/1.0" in c2.out
