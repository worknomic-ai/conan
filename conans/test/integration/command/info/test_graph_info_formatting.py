import pytest
from conans.test.utils.tools import TestClient, GenConanfile

def test_graph_info_text_stdout():
    client = TestClient()
    client.save({"conanfile.py": GenConanfile("pkg", "0.1")})
    client.run("create .")
    
    # Run graph info with text format
    client.run("graph info --requires=pkg/0.1 --format=text")
    
    assert "label: pkg/0.1" in client.stdout
    assert "label: pkg/0.1" not in client.stderr
    assert "Basic graph information" in client.stdout

def test_graph_info_conflict_escape():
    client = TestClient()
    client.save({
        "pkg_a1/conanfile.py": GenConanfile("pkg_a", "1.0"),
        "pkg_a2/conanfile.py": GenConanfile("pkg_a", "2.1"),
        "pkg_b/conanfile.py": GenConanfile("pkg_b", "1.0").with_requirement("pkg_a/[>=1.0 <2.0]"),
        "pkg_c/conanfile.py": GenConanfile("pkg_c", "1.0").with_requirement("pkg_a/[>2.0 <3.0]"),
        "conanfile.txt": "[requires]\npkg_b/1.0\npkg_c/1.0\n"
    })
    client.run("create pkg_a1")
    client.run("create pkg_a2")
    client.run("create pkg_b")
    client.run("create pkg_c")
    
    # Run graph info on conanfile.txt
    client.run("graph info . --format=text", assert_error=True)
    
    assert "\\[>2.0 <3.0\\]" in client.stderr

