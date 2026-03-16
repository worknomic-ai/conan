import json
from conans.test.utils.tools import TestClient

c = TestClient()
c.save({"myprofile": "[tool_requires]\nmytool/1.0.0"})
c.run("profile show -pr myprofile")
print("SUCCESS")
