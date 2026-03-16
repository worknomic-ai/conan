from conan.api.output import cli_out_write

def explain_conflict(graph):
    if not graph.error or not hasattr(graph.error, "require"):
        cli_out_write("No conflict found in the graph.")
        return

    err = graph.error
    cli_out_write("Version conflict found in graph:")
    
    node_ref = err.node.ref if err.node and err.node.ref else 'cli'
    
    # find who requires err.prev_node
    prev_origins = []
    if hasattr(err, "prev_node") and err.prev_node:
        for n in graph.nodes:
            for edge in n.dependencies:
                if edge.dst == err.prev_node:
                    ref = n.ref if n.ref else 'cli'
                    prev_origins.append(str(ref))
    
    if not prev_origins:
        orig = err.base_previous.ref if err.base_previous and err.base_previous.ref else 'cli'
        prev_origins = [str(orig)]

    cli_out_write(f"  Conflict originates from: {', '.join(prev_origins)}")
    cli_out_write(f"  Requirement 1: {err.prev_require.ref} (from {', '.join(prev_origins)})")
    cli_out_write(f"  Requirement 2: {err.require.ref} (from {node_ref})")

def _print_dict(data, indent):
    if isinstance(data, dict):
        for k, v in data.items():
            cli_out_write(f"{indent}{k}={v}")
    else:
        cli_out_write(f"{indent}{data}")

def explain_missing_binaries(conan_api, graph, remotes):
    from conans.client.graph.graph import BINARY_MISSING
    missing_nodes = [n for n in graph.nodes if n.binary == BINARY_MISSING]
    if not missing_nodes:
        cli_out_write("No missing binaries found in the graph.")
        return

    cli_out_write("Missing binaries explanation:")
    for node in missing_nodes:
        cli_out_write(f"  Node: {node.ref}")
        cli_out_write(f"  Requested package ID: {node.package_id}")
        
        # We can print requested settings/options
        cli_out_write("  Requested configuration:")
        if node.conanfile.settings:
            cli_out_write("    Settings:")
            for k, v in node.conanfile.settings.items():
                cli_out_write(f"      {k}={v}")
        if node.conanfile.options:
            cli_out_write("    Options:")
            for k, v in node.conanfile.options.items():
                cli_out_write(f"      {k}={v}")

        try:
            # fetch existing configurations
            prefs = conan_api.list.packages_configurations(node.ref)
            if not prefs and remotes:
                for remote in remotes:
                    try:
                        remote_prefs = conan_api.list.packages_configurations(node.ref, remote=remote)
                        if remote_prefs:
                            prefs.update(remote_prefs)
                    except Exception:
                        pass
            if not prefs:
                cli_out_write("  No existing binaries found for this reference.")
            else:
                cli_out_write("  Existing packages:")
                for pref, conf in prefs.items():
                    cli_out_write(f"    Package ID: {pref.package_id}")
                    settings = conf.get("info", {}).get("settings") or conf.get("settings")
                    if settings:
                        cli_out_write("      Settings:")
                        _print_dict(settings, "        ")
                    
                    options = conf.get("info", {}).get("options") or conf.get("options")
                    if options:
                        cli_out_write("      Options:")
                        _print_dict(options, "        ")
        except Exception as e:
            cli_out_write(f"  Could not fetch existing binaries: {e}")

