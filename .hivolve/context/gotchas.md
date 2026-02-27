## Custom Data Structures

`UserRequirementsDict` enforces a unified `__contains__` implementation to ensure consistent membership testing behavior.

## Dependency Resolution

Modifying package names via `replace_requires` in `GraphBuilder` can corrupt internal dictionary structures if keys are changed in-place. The established safe pattern is to rebuild requirement containers entirely when replacing requirements.

## Metadata Handling

Operations involving `replace_requires` must be followed by proper metadata updates and re-indexing to maintain consistency.

## Serialization

Profiles are now fully serializable to JSON.
