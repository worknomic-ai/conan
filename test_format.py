def format_define(define):
    if "=" in define:
        define = define.replace("=", "#", 1) # wait, what if multiple `=`? CL only allows `#` instead of first `=` or all?
        # Actually in original code it did `define = define.replace("=", "#")` replacing all!
        # Let's keep replacing all.
        pass

def format_define(define):
    # original replaced all '=' with '#'
    if "=" in define:
        define = define.replace("=", "#")
    
    # "Macro values with spaces are formatted with outer unescaped quotes."
    # If the original string had " " in it:
    if " " in define:
        # What about inner quotes?
        # In original: value.replace('"', r'\"')
        # If we use outer unescaped quotes, the string might look like:
        # "/DMY_MACRO#\"Hello World\""
        pass
