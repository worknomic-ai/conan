import os
import textwrap
from conans.client.profile_loader import ProfileLoader
from conans.test.utils.test_files import temp_folder
from conans.util.files import save
from conans.model.recipe_ref import RecipeReference

def test_profile_parse_replace_platform_requires():
    tmp = temp_folder()
    txt = textwrap.dedent("""
        [replace_requires]
        pkg/0.1: pkg/0.2
        other/*: other/1.0
        
        [platform_requires]
        libc/2.31
        libm/1.0
        """)
    profile_path = os.path.join(tmp, "profile.txt")
    save(profile_path, txt)

    profile_loader = ProfileLoader(cache_folder=temp_folder())
    profile = profile_loader.load_profile(profile_path)

    assert profile.replace_requires == {
        RecipeReference.loads("pkg/0.1"): RecipeReference.loads("pkg/0.2"),
        RecipeReference.loads("other/*"): RecipeReference.loads("other/1.0")
    }
    assert profile.platform_requires == [
        RecipeReference.loads("libc/2.31"),
        RecipeReference.loads("libm/1.0")
    ]

def test_profile_compose_replace_platform_requires():
    tmp = temp_folder()
    save(os.path.join(tmp, "profile0"), textwrap.dedent("""
        [replace_requires]
        pkg/0.1: pkg/0.2
        [platform_requires]
        libc/2.31
        """))
    save(os.path.join(tmp, "profile1"), textwrap.dedent("""
        [replace_requires]
        pkg/0.1: pkg/0.3
        other/1.0: other/1.1
        [platform_requires]
        libc/2.32
        libm/1.0
        """))

    profile_loader = ProfileLoader(cache_folder=temp_folder())
    p0 = profile_loader.load_profile(os.path.join(tmp, "profile0"))
    p1 = profile_loader.load_profile(os.path.join(tmp, "profile1"))
    
    p0.compose_profile(p1)

    assert p0.replace_requires == {
        RecipeReference.loads("pkg/0.1"): RecipeReference.loads("pkg/0.3"),
        RecipeReference.loads("other/1.0"): RecipeReference.loads("other/1.1")
    }
    # platform_requires merges by name, so libc/2.32 overrides libc/2.31
    assert p0.platform_requires == [
        RecipeReference.loads("libc/2.32"),
        RecipeReference.loads("libm/1.0")
    ]
