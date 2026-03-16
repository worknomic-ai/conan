import re
with open("conans/test/integration/toolchains/microsoft/test_nmakedeps.py", "r") as f:
    content = f.read()

content = content.replace('create . -s arch=x86_64', 'create . -s os=Windows -s arch=x86_64')
content = content.replace('install --requires=test-nmakedeps/1.0 -g NMakeDeps -s build_type=Release -s arch=x86_64', 'install --requires=test-nmakedeps/1.0 -g NMakeDeps -s os=Windows -s build_type=Release -s arch=x86_64')

with open("conans/test/integration/toolchains/microsoft/test_nmakedeps.py", "w") as f:
    f.write(content)
