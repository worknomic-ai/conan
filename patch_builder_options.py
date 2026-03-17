import sys

with open("conans/client/graph/graph_builder.py", "r") as f:
    content = f.read()

old_func = """        self._prepare_node(new_node, profile_host, profile_build, down_options)
        require.process_package_type(node, new_node)
        graph.add_node(new_node)"""

new_func = """        if new_node.recipe != RECIPE_SYSTEM_TOOL:
            self._prepare_node(new_node, profile_host, profile_build, down_options)
        require.process_package_type(node, new_node)
        graph.add_node(new_node)"""

if old_func not in content:
    print("Old function not found!")
    sys.exit(1)

content = content.replace(old_func, new_func)

with open("conans/client/graph/graph_builder.py", "w") as f:
    f.write(content)
