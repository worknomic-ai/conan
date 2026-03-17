import sys
from conans.conan import run
sys.argv = ['conan', 'graph', 'info', '.', '--format=text']
sys.exit(run())
