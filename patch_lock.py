with open("conans/model/graph_lock.py", "r") as f:
    lines = f.readlines()

out = []
for i, line in enumerate(lines):
    if line.strip() == "def deserialize(data):" and '""" constructs a GraphLock from a json like dict' in lines[i+1]:
        # we found deserialize in Lockfile. It's preceded by @staticmethod.
        # So we insert before @staticmethod (which is lines[i-1])
        out.insert(-1, """    def remove(self, requires=None, build_requires=None, python_requires=None):
        if requires:
            for r in requires:
                self._requires.remove(r)
        if build_requires:
            for r in build_requires:
                self._build_requires.remove(r)
        if python_requires:
            for r in python_requires:
                self._python_requires.remove(r)

""")
        out.append(line)
    else:
        out.append(line)

with open("conans/model/graph_lock.py", "w") as f:
    f.writelines(out)

