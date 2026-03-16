import os
import json
from unittest import mock

import pytest

from conan.tools.env.environment import _EnvValue
from conans.model.build_info import _Component
from conans.test.utils.tools import TestClient, GenConanfile


def test_deploy_absolute_path_different_drive():
    # Test _EnvValue
    env_val = _EnvValue("MYVAR", "/absolute/path", path=True)
    with mock.patch("os.path.relpath", side_effect=ValueError("cross-drive")):
        env_val.deploy_base_folder("/package", "/deploy")
    
    assert env_val._values[0] == "/absolute/path"

    # Test _Component
    comp = _Component(set_defaults=True)
    comp.includedirs = ["/absolute/include"]
    with mock.patch("os.path.relpath", side_effect=ValueError("cross-drive")):
        comp.deploy_base_folder("/package", "/deploy")

    assert comp.includedirs[0] == "/absolute/include"


def test_deployer_absolute_paths_cli():
    client = TestClient()
    conanfile = GenConanfile("pkg", "1.0").with_package_file("bin/pkg.dll", "content")
    conanfile.with_import("import os")
    
    abs_path = "C:/system/bin" if os.name == "nt" else "/system/bin"
    abs_path_include = "C:/system/include" if os.name == "nt" else "/system/include"
    
    conanfile.with_package_info(cpp_info={"bindirs": ["os.path.join(self.package_folder, 'bin')", f"'{abs_path}'"],
                                          "includedirs": ["os.path.join(self.package_folder, 'include')", f"'{abs_path_include}'"]},
                                env_info={"PATH": ["os.path.join(self.package_folder, 'bin')", f"'{abs_path}'"]})
    
    client.save({"conanfile.py": conanfile})
    client.run("create .")
    
    actual_relpath = os.path.relpath
    with mock.patch("os.path.relpath") as mock_relpath:
        def side_effect(path, start):
            if path in (abs_path, abs_path_include):
                raise ValueError("cross-drive")
            return actual_relpath(path, start)
        mock_relpath.side_effect = side_effect
        
        # Test full_deploy deployer
        client.run("install --requires=pkg/1.0 --deployer=full_deploy -g CMakeDeps")
        
        # Check that full_deploy preserved the path
        content = client.load("pkg-release-x86_64-data.cmake")
        assert abs_path_include in content
        assert f"full_deploy{abs_path_include}" not in content
        
        # Check that the internal package folders were properly relocated
        assert "full_deploy" in content
