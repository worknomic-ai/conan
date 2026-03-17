from conans.test.utils.tools import TestClient

client = TestClient()
client.save({"myprofile": "[tool_requires]\ncmake/3.20.0\n"})
client.run("profile show -pr myprofile --format=json", assert_error=True)
print("STDOUT:", client.out)
print("STDERR:", client.stderr)
