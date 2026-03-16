import pytest
import platform

# Mock platform.system() to return Windows
original_system = platform.system
platform.system = lambda: "Windows"

# Also need to mock some os.path or other things for vcvarsall.bat checking?
# Actually, TestClient uses temp dirs, let's see what breaks.
import sys
pytest.main(["-v", "/tmp/hivolve/878550cc-d78/member-d12b6bec-4f6/conans/test/integration/toolchains/microsoft/vcvars_test.py::test_vcvars_winsdk_version"])

platform.system = original_system
