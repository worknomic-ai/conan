## Dependency Specification

In the context of Lockfiles, `RecipeReference` matching logic for removal is specific: if a reference is provided without a revision in the key, it matches and removes the entry ignoring the locked revision. If a revision is specified, it requires an exact match.
