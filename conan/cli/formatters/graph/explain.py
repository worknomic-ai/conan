from conan.api.output import ConanOutput, cli_out_write
from conans.client.graph.graph_error import GraphConflictError, GraphMissingError
from conans.client.graph.graph import BINARY_MISSING

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

    conan_api = result.get("conan_api")
    graph = result.get("graph")
    
    missing_binaries = [n for n in graph.nodes if getattr(n, "binary", None) == BINARY_MISSING]
    
    if not missing_binaries:
        cli_out_write("Graph explanation: No errors found")
        return

    cli_out_write("Graph explanation: Missing binaries found")
    remotes = conan_api.remotes.list()

    for node in missing_binaries:
        cli_out_write(f"  Missing binary for: {node.ref}")
        
        # Query packages from cache and all remotes
        packages = conan_api.list.packages_configurations(node.ref, remote=None)
        for remote in remotes:
            try:
                remote_pkgs = conan_api.list.packages_configurations(node.ref, remote=remote)
                packages.update(remote_pkgs)
            except Exception:
                pass
                
        if not packages:
            cli_out_write("    No packages found for this recipe.")
            continue
            
        try:
            req_settings = node.conanfile.info.settings.serialize() if getattr(node.conanfile.info, "settings", None) else {}
        except Exception:
            req_settings = {}
            
        try:
            req_options = node.conanfile.info.options.serialize() if getattr(node.conanfile.info, "options", None) else {}
        except Exception:
            req_options = {}
            
        available_settings = {}
        available_options = {}
        
        for pkg_ref, pkg_info in packages.items():
            for k, v in pkg_info.get("settings", {}).items():
                available_settings.setdefault(k, set()).add(str(v))
            for k, v in pkg_info.get("options", {}).items():
                available_options.setdefault(k, set()).add(str(v))
                
        mismatches = []
        for k, v in req_settings.items():
            v_str = str(v)
            if k in available_settings and v_str not in available_settings[k]:
                avail = ", ".join(sorted(available_settings[k]))
                mismatches.append(f"Requested {k}={v_str}, but available are: {avail}")
                
        for k, v in req_options.items():
            v_str = str(v)
            if k in available_options and v_str not in available_options[k]:
                avail = ", ".join(sorted(available_options[k]))
                mismatches.append(f"Requested {k}={v_str}, but available are: {avail}")
                
        if mismatches:
            for m in mismatches:
                cli_out_write(f"    {m}")
        else:
            cli_out_write("    No exact settings/options mismatch found (could be missing due to profile or package ID mode).")
