from conans.model.recipe_ref import RecipeReference
transitive = RecipeReference.loads("target_pkg/1.2.3@user/channel")
print(RecipeReference("mytool", transitive.version, transitive.user, transitive.channel))
