import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-v", default=None, nargs='?', const="verbose")
print("empty:", parser.parse_args([]))
print("-v only:", parser.parse_args(["-v"]))
print("-vstatus:", parser.parse_args(["-vstatus"]))
