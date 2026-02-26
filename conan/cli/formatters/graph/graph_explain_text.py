from conan.api.output import ConanOutput, Color
from conans.client.graph.graph import BINARY_INVALID, RECIPE_CONSUMER, RECIPE_VIRTUAL


def format_graph_explain(result):
    graph = result["graph"]
    out = ConanOutput()

    out.title("Graph Explain")

    # 1. Version overrides and range resolutions
    if graph.resolved_ranges:
        out.writeln("Resolved version ranges:", Color.BRIGHT_WHITE)
        for r, s in graph.resolved_ranges.items():
            out.writeln(f"  {r} -> {s.repr_notime()}")

    overrides = graph.overrides()
    if overrides:
        out.writeln("Version overrides:", Color.BRIGHT_WHITE)
        for ref, ovs in overrides.items():
            for ov in ovs:
                if ov:
                    out.writeln(f"  {ref.repr_notime()} overridden to {ov.repr_notime()}")

    out.writeln("Binary Selection explanation:", Color.BRIGHT_WHITE)
    for node in graph.nodes:
        if node.recipe in (RECIPE_CONSUMER, RECIPE_VIRTUAL):
            continue

        out.writeln(f"  {node.ref.repr_notime()}:", Color.BRIGHT_CYAN)
        out.writeln(f"    Binary: {node.binary}", Color.BRIGHT_WHITE)

        if node.binary == BINARY_INVALID:
            if node.cant_build:
                out.writeln(f"    Invalid build: {node.cant_build}", Color.BRIGHT_RED)
            info_invalid = getattr(getattr(node.conanfile, "info", None), "invalid", None)
            if info_invalid:
                out.writeln(f"    Invalid configuration: {info_invalid}", Color.BRIGHT_RED)

        if node.binary_history:
            out.writeln("    History:", Color.BRIGHT_MAGENTA)
            for entry in node.binary_history:
                action = entry.get("action")
                if action == "remote_check":
                    status = entry.get("status")
                    remote = entry.get("remote")
                    pkg_id = entry.get("package_id")
                    out.writeln(f"      Remote '{remote}' check for '{pkg_id}': {status}")
                elif action == "compatible_packages":
                    out.writeln(f"      Checking compatible packages...")
                elif action == "compatible_check":
                    pkg_id = entry.get("package_id")
                    status = entry.get("status")
                    out.writeln(f"      Compatible '{pkg_id}': {status}")
