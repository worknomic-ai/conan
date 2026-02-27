## Custom Data Structures

`_LockRequires` internally utilizes `OrderedDict` to maintain the order of requirements. Operations on lockfile requirements (like removal via `pop`) rely on this structure to preserve graph stability.

## Dependency Resolution

`Requirement` objects within `conanfile.requires` are hashed by `(name, build_context)`. Modifying the reference name in-place within the dictionary corrupts the internal hash table. When replacing dependencies (e.g., via `[replace_requires]`), use a 'Copy-and-Rebuild' strategy: iterate the existing requirements and construct a completely new `OrderedDict` with new `Requirement` objects.

## Development Environment

Running integration tests (specifically in `conans/test/integration`) requires a specific set of dependencies that might be missing from a standard environment: `bottle`, `mock`, `webtest`, `parameterized`, and `colorama`.

## Metadata Handling

Operations involving `replace_requires` must be followed by proper metadata updates and re-indexing to maintain consistency.

## Serialization

Profiles are now fully serializable to JSON.
