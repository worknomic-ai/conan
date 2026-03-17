import json
from collections import defaultdict
d = defaultdict(dict)
d["a"]["b"] = 1
try:
    print(json.dumps(d))
except Exception as e:
    print("FAILED:", type(e), e)
