import json
import pytest
from conans.test.integration.graph.test_system_tools import save
from conans.test.assets.genconanfile import GenConanfile
from conans.test.utils.tools import TestClient

def test_platform_requires():
    client = TestClient()
    client.save({
        "conanfile.py": GenConanfile("pkg", "1.0").with_settings("os", "compiler", "build_type", "arch").with_require("dep/1.0").with_generator("CMakeDeps").with_generator("PkgConfigDeps"),
        "profile": "[platform_requires]\ndep/1.0"
    })
    client.run("install . -pr default -pr profile")
    print(client.out)
    assert "dep/1.0 - System tool" in client.out

def test_platform_requires_graph_info_json():
    client = TestClient()
    client.save({
        "transitive/conanfile.py": GenConanfile("transitive", "1.0"),
        "dep/conanfile.py": GenConanfile("dep", "1.0").with_require("transitive/1.0"),
        "conanfile.py": GenConanfile("app", "1.0").with_require("dep/1.0"),
        "profile": "[platform_requires]\ndep/1.0\n"
    })
    client.run("create transitive/conanfile.py")
    client.run("create dep/conanfile.py")
    client.run("graph info . -pr profile --format=json")
    
    graph_json = json.loads(client.stdout)
    nodes = graph_json["graph"]["nodes"]
    
    dep_node = None
    app_node = None
    transitive_node = None
    
    for node_id, node in nodes.items():
        if "app" in node.get("ref", ""):
            app_node = node
        elif "dep" in node.get("ref", ""):
            dep_node = node
        elif "transitive" in node.get("ref", ""):
            transitive_node = node
            
    assert app_node is not None
    assert dep_node is not None
    assert transitive_node is None  # transitive should be absent

    assert dep_node.get("recipe") == "System tool"
    assert dep_node.get("binary") == "System tool"



def test_platform_tool_requires():

    client = TestClient()
    client.save({
        "conanfile.py": GenConanfile("pkg", "1.0").with_settings("os", "compiler", "build_type", "arch").with_tool_requires("tool/1.0").with_generator("CMakeDeps").with_generator("PkgConfigDeps"),
        "profile": "[platform_tool_requires]\ntool/1.0"
    })
    client.run("install . -pr default -pr profile")
    print(client.out)
    assert "tool/1.0 - System tool" in client.out

