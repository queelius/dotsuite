import argparse
import json
import sys

try:
    import yaml
except ImportError:
    yaml = None

from . import set_, delete_, update_, append_

def main():
    """The main entry point for the dotmod command-line tool."""
    
    parser = argparse.ArgumentParser(
        prog="dotmod",
        description="Perform a single, immutable modification on a JSON or YAML document using a dot-path.",
        epilog="Use '-' for a filename to read from stdin. The modified document is written to stdout."
    )
    
    # --- Global arguments ---
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

    subparsers = parser.add_subparsers(dest='verb', required=True, help='The modification verb to apply.')

    # --- 'set' subcommand ---
    parser_set = subparsers.add_parser('set', help='Set a value at a path, creating it if necessary.')
    parser_set.add_argument('path', help="The dot-path for the value (e.g., 'user.name').")
    parser_set.add_argument('value', help="The value to set. Will be parsed as JSON or YAML.")

    # --- 'delete' subcommand ---
    parser_delete = subparsers.add_parser('delete', help='Delete a value at a path.')
    parser_delete.add_argument('path', help="The dot-path to delete (e.g., 'user.status').")

    # --- 'update' subcommand ---
    parser_update = subparsers.add_parser('update', help='Merge a JSON/YAML object into a dictionary at a path.')
    parser_update.add_argument('path', help="The dot-path to the target dictionary.")
    parser_update.add_argument('value', help="The JSON/YAML object string to merge (e.g., '{\"theme\":\"dark\"}').")

    # --- 'append' subcommand ---
    parser_append = subparsers.add_parser('append', help='Append a value to a list at a path.')
    parser_append.add_argument('path', help="The dot-path to the target list.")
    parser_append.add_argument('value', help="The JSON/YAML value string to append (e.g., '\"admin\"' or '123').")

    args = parser.parse_args()

    # --- Determine input format ---
    input_format = args.input_format
    if not input_format:
        if args.data_file != '-' and args.data_file.lower().endswith(('.yml', '.yaml')):
            input_format = 'yaml'
        else:
            input_format = 'json'

    if input_format == 'yaml' and not yaml:
        print("Error: PyYAML is not installed. Please install it with 'pip install PyYAML' to process YAML files.", file=sys.stderr)
        sys.exit(1)

    def load_data(filename, format):
        if filename == '-':
            content = sys.stdin.read()
        else:
            with open(filename, 'r') as f:
                content = f.read()
        
        if format == 'yaml':
            return yaml.safe_load(content)
        else:
            return json.loads(content)

    try:
        # --- Read Source Data ---
        data = load_data(args.data_file, input_format)

        # --- Execute Modification ---
        result = None
        if args.verb == 'delete':
            result = delete_(data, args.path)
        else:
            # For set, update, append, parse the value argument.
            # We use yaml.safe_load as it handles JSON as well as more permissive YAML.
            value_to_apply = yaml.safe_load(args.value) if yaml else json.loads(args.value)

            if args.verb == 'set':
                result = set_(data, args.path, value_to_apply)
            elif args.verb == 'update':
                if not isinstance(value_to_apply, dict):
                    raise TypeError("The 'update' verb requires a JSON/YAML object as its value.")
                result = update_(data, args.path, value_to_apply)
            elif args.verb == 'append':
                result = append_(data, args.path, value_to_apply)

        # --- Print Result ---
        if result is not None:
            if input_format == 'yaml':
                yaml.dump(result, sys.stdout)
            else:
                json.dump(result, sys.stdout)
                print() # Add a trailing newline

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}", file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        print(f"Error: Invalid format in input file - {e}", file=sys.stderr)
        sys.exit(1)
    except (TypeError, ValueError, IndexError) as e:
        print(f"Error: Modification failed - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
