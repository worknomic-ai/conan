import os
import pytest
from unittest.mock import patch, MagicMock
from conan.tools.files import ftp_download
from conan.errors import ConanException


class MockConanfile:
    pass


@patch("ftplib.FTP")
@patch("ftplib.FTP_TLS")
def test_ftp_download_secure(ftp_tls_mock, ftp_mock):
    conanfile = MockConanfile()
    
    # We mock FTP and FTP_TLS
    ftp_tls_instance = MagicMock()
    ftp_tls_mock.return_value = ftp_tls_instance
    
    # We patch open and os.unlink
    with patch("builtins.open", MagicMock()):
        with patch("os.path.split", return_value=("", "filename.txt")):
            ftp_download(conanfile, "host", "filename.txt", "login", "password", secure=True)
            
    # Verify FTP_TLS was called instead of FTP
    ftp_tls_mock.assert_called_once_with("host")
    ftp_mock.assert_not_called()
    
    # Verify standard methods were called on TLS instance
    ftp_tls_instance.login.assert_called_once_with("login", "password")
    ftp_tls_instance.prot_p.assert_called_once()
    ftp_tls_instance.retrbinary.assert_called_once()
    ftp_tls_instance.quit.assert_called_once()


@patch("ftplib.FTP")
@patch("ftplib.FTP_TLS")
def test_ftp_download_insecure(ftp_tls_mock, ftp_mock):
    conanfile = MockConanfile()
    
    # We mock FTP and FTP_TLS
    ftp_instance = MagicMock()
    ftp_mock.return_value = ftp_instance
    
    # We patch open and os.unlink
    with patch("builtins.open", MagicMock()):
        with patch("os.path.split", return_value=("", "filename.txt")):
            ftp_download(conanfile, "host", "filename.txt", "login", "password", secure=False)
            
    # Verify FTP was called instead of FTP_TLS
    ftp_mock.assert_called_once_with("host")
    ftp_tls_mock.assert_not_called()
    
    # Verify standard methods were called on FTP instance
    ftp_instance.login.assert_called_once_with("login", "password")
    # FTP does not have prot_p called
    assert not ftp_instance.prot_p.called
    ftp_instance.retrbinary.assert_called_once()
    ftp_instance.quit.assert_called_once()
