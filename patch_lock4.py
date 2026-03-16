with open("conans/model/graph_lock.py", "r") as f:
    content = f.read()

lockreq_remove = """
    def remove(self, pattern):
        to_remove = [ref for ref in self._requires if ref.matches(pattern, is_consumer=False)]
        for ref in to_remove:
            del self._requires[ref]
"""
content = content.replace("    def sort(self):", lockreq_remove + "\n    def sort(self):", 1)

lockfile_remove = """    def remove(self, requires=None, build_requires=None, python_requires=None):
        if requires:
            for r in requires:
                self._requires.remove(r)
        if build_requires:
            for r in build_requires:
                self._build_requires.remove(r)
        if python_requires:
            for r in python_requires:
                self._python_requires.remove(r)

"""

target = "    @staticmethod\n    def deserialize(data):"
parts = content.split(target)
if len(parts) == 3:
    content = parts[0] + target + parts[1] + lockfile_remove + target + parts[2]
else:
    print("Not exactly 3 parts:", len(parts))

with open("conans/model/graph_lock.py", "w") as f:
    f.write(content)

