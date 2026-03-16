from unittest import mock
import os
import pytest

from conan.tools.scm import Git

def test_is_dirty_scoped():
    conanfile_mock = mock.MagicMock()
    conanfile_mock.build_folder = "/path/to/build"
    conanfile_mock.folders.base_source = "/path/to/source"
    
    git = Git(conanfile_mock, folder="/path/to/source")
    
    with mock.patch("conan.tools.scm.git.Git.run") as run_mock:
        run_mock.return_value = " M some_file.txt"
        
        is_dirty = git.is_dirty()
        
        run_mock.assert_called_once_with("status . -s")
        assert is_dirty is True

    with mock.patch("conan.tools.scm.git.Git.run") as run_mock:
        run_mock.return_value = ""
        
        is_dirty = git.is_dirty()
        
        run_mock.assert_called_once_with("status . -s")
        assert is_dirty is False
