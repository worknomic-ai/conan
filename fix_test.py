with open("conans/test/integration/graph/test_profile_overrides.py", "r") as f:
    content = f.read()

content = content.replace('"[replace_requires]\ntransitive/*: mydep/1.0"', '"[replace_requires]\\ntransitive/*: mydep/1.0"')

with open("conans/test/integration/graph/test_profile_overrides.py", "w") as f:
    f.write(content)
