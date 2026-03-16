import pytest
from conans.test.utils.tools import TestClient, GenConanfile

def test_graph_explain_conflict():
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
    
    # Run graph explain on conanfile.txt
    client.run("graph explain .", assert_error=True)
    
    assert "pkg_b/1.0" in client.stdout
    assert "pkg_c/1.0" in client.stdout

def test_graph_explain_missing_binary():
    client = TestClient()
    client.save({
        "conanfile.py": GenConanfile("pkg", "0.1").with_settings("os")
    })
    client.run("create . -s os=Linux")
    
    client.run("graph explain --requires=pkg/0.1 -s os=Windows")
    
    # It should show missing binary and mention existing Linux package
    assert "Missing binaries" in client.stdout
    assert "os=Windows" in client.stdout
    assert "os=Linux" in client.stdout

