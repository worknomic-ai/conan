import argparse

class MyParser(argparse.ArgumentParser):
    def parse_args(self, args=None, namespace=None):
        print("OVERRIDE parse_args")
        return super().parse_args(args, namespace)

parser = MyParser()
parser.add_argument("-v")
print("Calling parse_known_args...")
parser.parse_known_args(["-v", "debug"])
print("Calling parse_args...")
parser.parse_args(["-v", "debug"])
