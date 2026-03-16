with open("conan/cli/commands/lock.py", "r") as f:
    content = f.read()

remove_cmd = """
@conan_subcommand()
def lock_remove(conan_api, parser, subparser, *args):
    \"\"\"
    Remove requires, build-requires or python-requires from an existing lockfile.
    References can be supplied with and without revisions like "--requires=pkg/version",
    and they can contain patterns like "--requires=pkg/*".
    \"\"\"
    subparser.add_argument('--requires', action="append", help='Remove references from lockfile.')
    subparser.add_argument('--build-requires', action="append",
                           help='Remove build-requires from lockfile')
    subparser.add_argument('--python-requires', action="append",
                           help='Remove python-requires from lockfile')
    subparser.add_argument("--lockfile-out", action=OnceArgument, default=LOCKFILE,
                           help="Filename of the created lockfile")
    subparser.add_argument("--lockfile", action=OnceArgument, required=True,
                           help="Filename of the input lockfile")
    args = parser.parse_args(*args)

    lockfile = conan_api.lockfile.get_lockfile(lockfile=args.lockfile, partial=True)

    lockfile.remove(requires=args.requires,
                    build_requires=args.build_requires,
                    python_requires=args.python_requires)
    conan_api.lockfile.save_lockfile(lockfile, args.lockfile_out)
"""

content += remove_cmd

with open("conan/cli/commands/lock.py", "w") as f:
    f.write(content)
