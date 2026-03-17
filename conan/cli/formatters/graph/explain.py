from conan.api.output import ConanOutput
from conans.client.graph.graph_error import GraphConflictError, GraphMissingError
from conans.client.graph.graph import BINARY_MISSING

def print_graph_explain(result):
    error = result.get("error")
    if error:
        ConanOutput().info("Graph error explanation:")
        if isinstance(error, GraphConflictError):
            ConanOutput().info("  Conflict detected")
        elif isinstance(error, GraphMissingError):
            ConanOutput().info("  Missing dependency detected")
        else:
            ConanOutput().info(f"  {error}")
        return

    conan_api = result.get("conan_api")
    graph = result.get("graph")
    
    missing_binaries = [n for n in graph.nodes if getattr(n, "binary", None) == BINARY_MISSING]
    
    if not missing_binaries:
        ConanOutput().info("Graph explanation: No errors found")
        return

    ConanOutput().info("Graph explanation: Missing binaries found")
    remotes = conan_api.remotes.list()

    for node in missing_binaries:
        ConanOutput().info(f"  Missing binary for: {node.ref}")
        
        # Query packages from cache and all remotes
        packages = conan_api.list.packages_configurations(node.ref, remote=None)
        for remote in remotes:
            try:
                remote_pkgs = conan_api.list.packages_configurations(node.ref, remote=remote)
                packages.update(remote_pkgs)
            except Exception:
                pass
                
        if not packages:
            ConanOutput().info("    No packages found for this recipe.")
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
                ConanOutput().info(f"    {m}")
        else:
            ConanOutput().info("    No exact settings/options mismatch found (could be missing due to profile or package ID mode).")

