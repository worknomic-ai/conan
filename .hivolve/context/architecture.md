## Build Helpers

Generators like `VCVars` must retrieve SDK versions and other settings from the `conanfile.conf` (e.g., `tools.microsoft:winsdk_version`) rather than relying on hardcoded defaults in the generator code. This ensures configuration flows correctly from profiles/conf to the generated environment scripts.

## Cache Layer

The cache system implements cross-platform portability by creating platform-agnostic archives. This is achieved through path normalization, stripping system-specific metadata, and standardizing file permissions before archiving, allowing restoration across different OS layouts.

## Configuration

The `CONAN_LOG_LEVEL` environment variable controls logging verbosity. It has lower precedence than explicit CLI flags but overrides the default verbosity setting.

## Dependency Resolution

Dependency replacement logic (`[replace_requires]` and `[replace_tool_requires]`) is executed in `DepsGraphBuilder._prepare_node`, strictly after the `configure()` method runs but before requirement expansion. This ensures that replacements defined in profiles override recipe definitions before the graph is traversed further.

## Lockfile Management

The `conan lock remove` command implementation follows the standard CLI -> API -> Model pattern. The CLI delegates to `LockfileAPI.remove_lockfile`, which bridges to the `Lockfile` model. The `Lockfile` model further delegates the actual removal logic to `_LockRequires` containers for `requires`, `build_requires`, and `python_requires`.

## Output Management

Logging levels obey a strict precedence hierarchy: CLI arguments > Environment variables (`CONAN_LOG_LEVEL`) > Defaults.

## Recipe Interface

The `self.dependencies` attribute supports the `in` operator, allowing recipes to check for the existence of specific dependencies programmatically.
