import os
from unittest import mock

import pytest

from conan.tools.env.environment import _EnvValue
from conans.model.build_info import _Component
from conans.test.utils.tools import TestClient, GenConanfile


def test_deploy_absolute_path_different_drive():
    # Test _EnvValue
    env_val = _EnvValue("MYVAR", "D:/absolute/path", path=True)
    with mock.patch("os.path.relpath", side_effect=ValueError("cross-drive")):
        env_val.deploy_base_folder("C:/package", "C:/deploy")
    
    assert env_val._values[0] == os.path.join("C:/deploy", "D:/absolute/path")

    # Test _Component
    comp = _Component(set_defaults=True)
    comp.includedirs = ["D:/absolute/include"]
    with mock.patch("os.path.relpath", side_effect=ValueError("cross-drive")):
        comp.deploy_base_folder("C:/package", "C:/deploy")

    assert comp.includedirs[0] == os.path.join("C:/deploy", "D:/absolute/include")

def test_deployer_absolute_paths_cli():
    client = TestClient()
    conanfile = GenConanfile("pkg", "1.0").with_package_file("bin/pkg.dll", "content")
    conanfile.with_import("import os")
    conanfile.with_package_info(cpp_info={"bindirs": ["os.path.join(self.package_folder, 'bin')", "'D:/system/bin'"]},
                                env_info={"PATH": ["os.path.join(self.package_folder, 'bin')", "'D:/system/bin'"]})
    
    client.save({"conanfile.py": conanfile})
    client.run("create .")
    
    actual_relpath = os.path.relpath
    with mock.patch("os.path.relpath") as mock_relpath:
        def side_effect(path, start):
            if path == "D:/system/bin":
                raise ValueError("cross-drive")
            return actual_relpath(path, start)
        mock_relpath.side_effect = side_effect
        
        # Test full_deploy deployer
        client.run("install --requires=pkg/1.0 --deployer=full_deploy")
        # Should not crash
