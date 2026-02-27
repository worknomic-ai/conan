## Command Line Interface

To support a precedence chain of CLI Flag > Environment Variable > Default Value, CLI arguments must be defined with `default=None` in `argparse`. The environment variable check and fallback to the hard default should happen explicitly in the parsing logic (e.g., `ConanArgumentParser.parse_args`) only when the CLI argument is `None`. Setting a hard default in `add_argument` prevents distinguishing between an explicit user flag and the default behavior.

## Error Handling

Validation logic, particularly for environment variables like `CONAN_LOG_LEVEL`, enforces a specific convention for error message formatting to maintain consistency across the CLI.
