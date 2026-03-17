from conan.api.output import ConanOutput
from conans.client.graph.graph_error import GraphConflictError, GraphMissingError

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

    # In the future, this module will also explain missing binaries
    ConanOutput().info("Graph explanation: No errors found")

