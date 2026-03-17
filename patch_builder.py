import sys

with open("conans/client/graph/graph_builder.py", "r") as f:
    content = f.read()

old_func = """    @staticmethod
    def _resolved_system_tool(node, require, profile_build, profile_host, resolve_prereleases):
        if node.context == CONTEXT_HOST and not require.build:  # Only for DIRECT tool_requires
            return
        system_tool = profile_build.system_tools if node.context == CONTEXT_BUILD \\
            else profile_host.system_tools
        if system_tool:
            version_range = require.version_range
            for d in system_tool:
                if require.ref.name == d.name:
                    if version_range:
                        if version_range.contains(d.version, resolve_prereleases):
                            require.ref.version = d.version  # resolved range is replaced by exact
                            return d, ConanFile(str(d)), RECIPE_SYSTEM_TOOL, None
                    elif require.ref.version == d.version:
                        if d.revision is None or require.ref.revision is None or \\
                                d.revision == require.ref.revision:
                            require.ref.revision = d.revision
                            return d, ConanFile(str(d)), RECIPE_SYSTEM_TOOL, None"""

new_func = """    @staticmethod
    def _resolved_system_tool(node, require, profile_build, profile_host, resolve_prereleases):
        profile = profile_build if node.context == CONTEXT_BUILD else profile_host
        
        if require.build:
            # tool_requires use platform_tool_requires + system_tools
            platform_requires = profile.platform_tool_requires + profile.system_tools
        else:
            # regular requires use platform_requires
            platform_requires = profile.platform_requires

        if platform_requires:
            version_range = require.version_range
            for d in platform_requires:
                if require.ref.name == d.name:
                    if version_range:
                        if version_range.contains(d.version, resolve_prereleases):
                            require.ref.version = d.version  # resolved range is replaced by exact
                            return d, ConanFile(str(d)), RECIPE_SYSTEM_TOOL, None
                    elif require.ref.version == d.version:
                        if d.revision is None or require.ref.revision is None or \\
                                d.revision == require.ref.revision:
                            require.ref.revision = d.revision
                            return d, ConanFile(str(d)), RECIPE_SYSTEM_TOOL, None"""

if old_func not in content:
    print("Old function not found!")
    sys.exit(1)

content = content.replace(old_func, new_func)

with open("conans/client/graph/graph_builder.py", "w") as f:
    f.write(content)
