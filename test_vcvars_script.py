import sys
import os

from conan.tools.microsoft import visual

visual.os.path.isdir = lambda x: True

cmd = visual.vcvars_command("16", architecture="amd64", platform_type=None,
                        winsdk_version="10.0.19041.0", vcvars_ver="14.2",
                        vs_install_path="C:\\VS\\")
print(cmd)

cmd_no_sdk = visual.vcvars_command("16", architecture="amd64", platform_type=None,
                        winsdk_version=None, vcvars_ver="14.2",
                        vs_install_path="C:\\VS\\")
print(cmd_no_sdk)
