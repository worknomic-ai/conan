def format_define(define):
    if "=" in define:
        define = define.replace("=", "#")
    
    define = define.replace('"', r'\"')
    
    flag = f"/D{define}"
    if " " in flag:
        return f'"{flag}"'
    return flag

defines = [
    ("WITHOUT_SPACE=NO_SPACE", "/DWITHOUT_SPACE#NO_SPACE"),
    ("WITH_SPACE=VALUE WITH SPACES", '"/DWITH_SPACE#VALUE WITH SPACES"'),
    ("MULTIPLE_EQUALS=VALUE=WITH=EQUALS", "/DMULTIPLE_EQUALS#VALUE#WITH#EQUALS"),
    ('MY_MACRO="Hello World"', '"/DMY_MACRO#\\"Hello World\\""'),
    ("MACRO_WITH_NO_EQUALS BUT HAS SPACES", '"/DMACRO_WITH_NO_EQUALS BUT HAS SPACES"'),
    ("MACRO_WITH_NO_EQUALS_AND_NO_SPACES", "/DMACRO_WITH_NO_EQUALS_AND_NO_SPACES")
]

for d, expected in defines:
    res = format_define(d)
    print(f"Original: {d}")
    print(f"Formatted: {res}")
    print(f"Expected:  {expected}")
    if res != expected:
        print("MISMATCH!")
    print("---")