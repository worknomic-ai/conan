import unittest
from conans.model.build_info import CppInfo

class CppInfoInheritanceTest(unittest.TestCase):
    def test_component_inherits_global_values(self):
        cpp_info = CppInfo(set_defaults=False)
        cpp_info.includedirs = ["my_include"]
        cpp_info.libdirs = ["my_lib"]
        cpp_info.cflags = ["-myflag"]
        cpp_info.sysroot = "my_sysroot"
        
        # Accessing components should inherit these
        self.assertEqual(cpp_info.components["mycomp"].includedirs, ["my_include"])
        self.assertEqual(cpp_info.components["mycomp"].libdirs, ["my_lib"])
        self.assertEqual(cpp_info.components["mycomp"].cflags, ["-myflag"])
        self.assertEqual(cpp_info.components["mycomp"].sysroot, "my_sysroot")

        # But requires shouldn't be inherited? Or maybe it should? Let's assume yes or no
        # Actually wait, let's see if mutating the inherited list mutates the global one
        cpp_info.components["mycomp"].includedirs.append("other_include")
        self.assertEqual(cpp_info.components["mycomp"].includedirs, ["my_include", "other_include"])
        self.assertEqual(cpp_info.includedirs, ["my_include"]) # Should not mutate global!

    def test_component_serialize_deserialize(self):
        info = CppInfo(set_defaults=False)
        info.includedirs = ["include"]
        info.components["mycomp"]

        content = info.serialize()
        new_info = CppInfo().deserialize(content)
        self.assertEqual(new_info.includedirs, ["include"])
        self.assertEqual(new_info.components["mycomp"].includedirs, ["include"])

    def test_component_inherits_with_defaults(self):
        info = CppInfo(set_defaults=True)
        info.includedirs = ["my_include"]
        # Accessing components should inherit the updated global value instead of sticking to 'include'
        self.assertEqual(info.components["mycomp"].includedirs, ["my_include"])
