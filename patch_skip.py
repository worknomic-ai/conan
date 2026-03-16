import re
with open("conans/test/integration/toolchains/microsoft/test_nmakedeps.py", "r") as f:
    content = f.read()

content = content.replace('@pytest.mark.skipif(platform.system() != "Windows", reason="Only for windows")', '')

with open("conans/test/integration/toolchains/microsoft/test_nmakedeps.py", "w") as f:
    f.write(content)
