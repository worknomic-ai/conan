import os
import re

file_path = "conan/tools/microsoft/nmakedeps.py"
with open(file_path, "r") as f:
    content = f.read()

def _quote_if_spaces(text):
    return f'"{text}"' if ' ' in text and '"' not in text else text

# modify link_args
content = content.replace('ret.extend(cpp_info.exelinkflags or [])', 'ret.extend([_quote_if_spaces(f) for f in cpp_info.exelinkflags or []])')
content = content.replace('ret.extend(cpp_info.sharedlinkflags or [])', 'ret.extend([_quote_if_spaces(f) for f in cpp_info.sharedlinkflags or []])')
content = content.replace('ret.extend([format_lib(lib) for lib in cpp_info.libs or []])', 'ret.extend([_quote_if_spaces(format_lib(lib)) for lib in cpp_info.libs or []])')
content = content.replace('ret.extend([format_lib(lib) for lib in cpp_info.system_libs or []])', 'ret.extend([_quote_if_spaces(format_lib(lib)) for lib in cpp_info.system_libs or []])')

# modify cl_flags
content = content.replace('cl_flags.extend(cpp_info.cflags or [])', 'cl_flags.extend([_quote_if_spaces(f) for f in cpp_info.cflags or []])')
content = content.replace('cl_flags.extend(cpp_info.cxxflags or [])', 'cl_flags.extend([_quote_if_spaces(f) for f in cpp_info.cxxflags or []])')
content = content.replace('cl_flags.extend([format_define(define) for define in cpp_info.defines or []])', 'cl_flags.extend([_quote_if_spaces(format_define(define)) for define in cpp_info.defines or []])')

# inject _quote_if_spaces
inject_idx = content.find('def format_lib(lib):')
content = content[:inject_idx] + '''def _quote_if_spaces(text):
                return f\'"{text}"\' if \' \' in text and \'"\' not in text else text

            ''' + content[inject_idx:]

with open(file_path, "w") as f:
    f.write(content)

