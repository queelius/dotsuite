import argparse
import json
import sys
import yaml

from .core import check

def main():
    parser = argparse.ArgumentParser(
        prog="dotany",
        description="Check if any value found by a dotpath query satisfies a condition."
    )
    parser.add_argument("path", help="The dotpath query string.")
    parser.add_argument("--equals", required=True, help="The value to check for equality.")
    parser.add_argument(
        'data_file',
        nargs='?',
        default='-',
        help="Path to the source JSON or YAML data file, or '-' for stdin (default)."
    )
    args = parser.parse_args()

    try:
        if args.data_file == '-':
            data = yaml.safe_load(sys.stdin)
        else:
            with open(args.data_file, 'r') as f:
                data = yaml.safe_load(f)

        # The value from the command line is a string, we may need to coerce it
        # For now, we'll just compare it as a string, but a full implementation
        # might need type coercion (like in dotpath).
        equals_value = args.equals

        if check(data, args.path, equals=equals_value):
            sys.exit(0)
        else:
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
