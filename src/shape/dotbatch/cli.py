import argparse
import json
import sys

try:
    import yaml
except ImportError:
    yaml = None

from .core import apply

def main():
    """The main entry point for the dotbatch command-line tool."""
    
    parser = argparse.ArgumentParser(
        prog="dotbatch",
        description="Apply a declarative changeset of modifications to a JSON or YAML document.",
        epilog="Use '-' for a filename to read from stdin. The modified document is written to stdout."
    )
    
    parser.add_argument(
        'changeset_file',
        help="Path to the JSON or YAML file containing the list of operations DSL, or '-' for stdin."
    )
    
    parser.add_argument(
        'data_file',
        nargs='?',
        default='-',
        help="Path to the source JSON or YAML data file, or '-' for stdin (default)."
    )

    parser.add_argument(
        '--in', '--input-format', dest='input_format',
        choices=['json', 'yaml'],
        help="Format of the input files. If not provided, it's inferred from file extensions. Defaults to 'json' for stdin or unknown file types."
    )
    
    args = parser.parse_args()

    def infer_format(filename, default='json'):
        if args.input_format:
            return args.input_format
        if filename != '-' and filename.lower().endswith((".yml", ".yaml")):
            return 'yaml'
        return default

    changeset_format = infer_format(args.changeset_file)
    data_format = infer_format(args.data_file)

    if (changeset_format == 'yaml' or data_format == 'yaml') and not yaml:
        print("Error: PyYAML is not installed. Please install it with 'pip install PyYAML' to process YAML files.", file=sys.stderr)
        sys.exit(1)

    def load_content(filename):
        if filename == '-':
            return sys.stdin.read()
        else:
            with open(filename, 'r') as f:
                return f.read()

    def parse_content(content, format):
        if format == 'yaml':
            return yaml.safe_load(content)
        return json.loads(content)

    try:
        # --- Read File Contents ---
        if args.changeset_file == '-' and args.data_file == '-':
            print("Error: Cannot read both changeset and data from stdin.", file=sys.stderr)
            sys.exit(1)

        changeset_content = load_content(args.changeset_file)
        # If changeset was stdin, data must be a file. If data is also stdin, we've already exited.
        data_content = load_content(args.data_file)

        # --- Parse Contents ---
        changeset_dsl = parse_content(changeset_content, changeset_format)
        data = parse_content(data_content, data_format)

        # --- Execute Transformation ---
        result = apply(data, changeset_dsl)

        # --- Print Result ---
        if data_format == 'yaml':
            yaml.dump(result, sys.stdout)
        else:
            json.dump(result, sys.stdout)
            print()

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}", file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        print(f"Error: Invalid format in input file - {e}", file=sys.stderr)
        sys.exit(1)
    except (TypeError, ValueError) as e:
        print(f"Error: Batch execution failed - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()