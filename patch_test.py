import re
with open("conans/test/integration/toolchains/microsoft/test_nmakedeps.py", "r") as f:
    content = f.read()

content = content.replace(
    "@pytest.mark.skipif(platform.system() != \"Windows\", reason=\"Only for windows\")",
    "import mock\n@mock.patch(\"platform.system\", return_value=\"Windows\")"
)

content = content.replace(
    "def test_nmakedeps():",
    "def test_nmakedeps(mock_system):"
)

with open("conans/test/integration/toolchains/microsoft/test_nmakedeps.py", "w") as f:
    f.write(content)
