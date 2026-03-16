def _quote_if_spaces(text):
    return f'"{text}"' if ' ' in text and '"' not in text else text

print(_quote_if_spaces('/DFOO#\\"bar baz\\"'))
print(_quote_if_spaces('-IC:\\My Path'))
print(_quote_if_spaces('my lib.lib'))
