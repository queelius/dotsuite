import argparse
import json
import sys
import yaml
from .dotstar import search, find_all

def main():
    parser = argparse.ArgumentParser(description="Search nested data with wildcard patterns.")
    parser.add_argument("pattern", help="Dot-notation pattern with wildcards (*).")
    parser.add_argument("--find", action="store_true", help="Output (path, value) tuples instead of just values.")
    parser.add_argument('--input-format', choices=['json', 'yaml'], default='json', help='Input format (default: json)')

    args = parser.parse_args()

    try:
        if args.input_format == 'yaml':
            data = yaml.safe_load(sys.stdin)
        else:
            data = json.load(sys.stdin)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        print(f"Error: Invalid {args.input_format.upper()} input. {e}", file=sys.stderr)
        sys.exit(1)


    if args.find:
        results = find_all(data, args.pattern)
        # Convert tuples to lists for consistent YAML/JSON output
        results = [list(item) for item in results]
    else:
        results = search(data, args.pattern)

    # Output should match input format
    if args.input_format == 'yaml':
        yaml.dump(results, sys.stdout, default_flow_style=False)
    else:
        json.dump(results, sys.stdout, indent=2)

if __name__ == "__main__":
    main()
