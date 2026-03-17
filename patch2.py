import re

with open('conans/client/graph/graph_builder.py', 'r') as f:
    content = f.read()

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
                            node.conanfile.requires._requires = OrderedDict((v.ref.name, v) if hasattr(v, 'ref') and hasattr(v.ref, 'name') else (v, v) for v in req_values)
                            node.transitive_deps = OrderedDict((v.require.ref.name, v) if hasattr(v, 'require') and hasattr(v.require, 'ref') and hasattr(v.require.ref, 'name') else (v.require, v) for v in dep_values)"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('conans/client/graph/graph_builder.py', 'w') as f:
        f.write(content)
    print("Patched!")
else:
    print("Could not find old code!")
