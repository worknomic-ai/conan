from conan.api.output import ConanOutput, cli_out_write
from conans.client.graph.graph_error import GraphConflictError, GraphMissingError

def _get_path(node):
    path = []
    current = node
    while current:
        path.append(current)
        if not current.dependants:
            break
        current = current.dependants[0].src
    return list(reversed(path))

def _format_path(path, require):
    res = " -> ".join(str(n.ref) if n.ref else n.conanfile.display_name for n in path)
    if require:
        res += f" -> {require.ref}"
    return res

def print_graph_explain(result):
    error = result.get("error")
    if error:
        ConanOutput().info("Graph error explanation:")
        if isinstance(error, GraphConflictError):
            cli_out_write("  Conflict detected:")
            
            node = error.node
            require = error.require
            prev_node = error.prev_node
            prev_require = error.prev_require
            base_previous = error.base_previous
            
            path1 = _get_path(node)
            path1_str = _format_path(path1, require)
            
            if prev_node:
                if prev_node.dependants:
                    prev_parent = prev_node.dependants[0].src
                    path2 = _get_path(prev_parent)
                    path2_str = _format_path(path2, prev_require)
                else:
                    path2 = _get_path(prev_node)
                    path2_str = _format_path(path2, prev_require)
            else:
                path2 = _get_path(base_previous)
                path2_str = _format_path(path2, prev_require)
                
            cli_out_write(f"    {path2_str}")
            cli_out_write(f"    {path1_str}")
            
        elif isinstance(error, GraphMissingError):
            ConanOutput().info("  Missing dependency detected")
        else:
            ConanOutput().info(f"  {error}")
        return

    # In the future, this module will also explain missing binaries
    ConanOutput().info("Graph explanation: No errors found")
