import re

with open('conans/client/graph/graph_builder.py', 'r') as f:
    content = f.read()

# Replace:
# req_items = list(node.conanfile.requires._requires.items())
# dep_items = list(node.transitive_deps.items())
# ...
# node.conanfile.requires._requires = OrderedDict(req_items)
# node.transitive_deps = OrderedDict(dep_items)
#
# With:
# req_values = list(node.conanfile.requires._requires.values())
# dep_values = list(node.transitive_deps.values())
# ...
# node.conanfile.requires._requires = OrderedDict((r.ref, r) for r in req_values)
# node.transitive_deps = OrderedDict((r.require.ref, r) for r in dep_values)

old_code = """                            req_items = list(node.conanfile.requires._requires.items())
                            dep_items = list(node.transitive_deps.items())
                            
                            # apply substitution
                            require.ref = copy.copy(replace_require_list[0])
                            
                            # safe rebuild
                            node.conanfile.requires._requires = OrderedDict(req_items)
                            node.transitive_deps = OrderedDict(dep_items)"""

new_code = """                            req_values = list(node.conanfile.requires._requires.values())
                            dep_values = list(node.transitive_deps.values())
                            
                            # apply substitution
                            require.ref = copy.copy(replace_require_list[0])
                            
                            # safe rebuild
                            node.conanfile.requires._requires = OrderedDict((r.ref, r) for r in req_values)
                            node.transitive_deps = OrderedDict((r.require.ref, r) for r in dep_values)"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('conans/client/graph/graph_builder.py', 'w') as f:
        f.write(content)
    print("Patched!")
else:
    print("Could not find old code!")
