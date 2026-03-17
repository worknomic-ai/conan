from collections import OrderedDict

class Requirement:
    def __init__(self, name):
        self.name = name
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return self.name == other.name

req1 = Requirement("a")
d = OrderedDict()
d[req1] = req1

req_items = list(d.items())
req1.name = "b"
d2 = OrderedDict(req_items)

print("d2 keys:", [k.name for k in d2.keys()])
# Can we look up "b" in d2?
req_b = Requirement("b")
print("lookup b:", req_b in d2)

# But wait, does it work with the exact objects?
print("d2[req_b] is req1:", d2[req_b] is req1)
