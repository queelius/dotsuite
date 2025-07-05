import argparse
import json
import sys

try:
    import yaml
except ImportError:
    yaml = None

from . import get

def main():
    """The main entry point for the dotget command-line tool."""
    
    parser = argparse.ArgumentParser(
        prog="dotget",
        description="Get a single value from a JSON or YAML document using an exact dot-path.",
        epilog="Use '-' for the data file to read from stdin. The result is written to stdout as JSON or YAML."
    )
    
    parser.add_argument(
        'path',
        help="The exact dot-path for the value (e.g., 'user.name')."
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
        help="Format of the input data. If not provided, it's inferred from the file extension. Defaults to 'json' for stdin or unknown file types."
    )
    
    args = parser.parse_args()

    input_format = args.input_format
    if not input_format:
        if args.data_file != '-' and args.data_file.lower().endswith(('.yml', '.yaml')):
            input_format = 'yaml'
        else:
            input_format = 'json'

    if input_format == 'yaml' and not yaml:
        print("Error: PyYAML is not installed. Please install it with 'pip install PyYAML' to process YAML files.", file=sys.stderr)
        sys.exit(1)

    try:
        # --- Read Source Data ---
        if args.data_file == '-':
            content = sys.stdin.read()
        else:
            with open(args.data_file, 'r') as f:
                content = f.read()

        if input_format == 'yaml':
            data = yaml.safe_load(content)
        else:
            data = json.loads(content)

        # --- Execute Query ---
        result = get(data, args.path)

        # --- Print Result ---
        if input_format == 'yaml':
            yaml.dump(result, sys.stdout)
        else:
            json.dump(result, sys.stdout)
            print()

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}", file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        print(f"Error: Invalid format in input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
