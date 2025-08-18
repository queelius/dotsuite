#!/usr/bin/env python3
"""
Command-line interface for dotequals.

Usage:
    dotequals data.json user.role admin
    echo '{"status": "active"}' | dotequals - status active
    
Exit codes:
    0 - Path exists and equals the value
    1 - Path doesn't exist or doesn't equal the value
"""

import sys
import json
import argparse
from .core import equals, not_equals, equals_any


def main():
    parser = argparse.ArgumentParser(
        description="Check if a JSON path has a specific value"
    )
    parser.add_argument(
        "input",
        help="JSON file path or '-' for stdin"
    )
    parser.add_argument(
        "path",
        help="Dot notation path to check"
    )
    parser.add_argument(
        "value",
        help="Expected value (will be parsed as JSON if possible)"
    )
    parser.add_argument(
        "--not", "-n",
        dest="invert",
        action="store_true",
        help="Check if path does NOT equal the value"
    )
    parser.add_argument(
        "--any", "-a",
        nargs="*",
        dest="any_values",
        help="Additional values for equals_any check"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print result message"
    )
    
    args = parser.parse_args()
    
    # Read input
    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        with open(args.input, "r") as f:
            data = json.load(f)
    
    # Parse value as JSON if possible
    try:
        value = json.loads(args.value)
    except json.JSONDecodeError:
        value = args.value
    
    # Check equality
    if args.any_values is not None:
        # Parse additional values
        values = [value]
        for v in args.any_values:
            try:
                values.append(json.loads(v))
            except json.JSONDecodeError:
                values.append(v)
        result = equals_any(data, args.path, *values)
    elif args.invert:
        result = not_equals(data, args.path, value)
    else:
        result = equals(data, args.path, value)
    
    # Output
    if args.verbose:
        if result:
            print(f"✓ Path '{args.path}' {'does not equal' if args.invert else 'equals'} {args.value}")
        else:
            print(f"✗ Path '{args.path}' {'equals' if args.invert else 'does not equal'} {args.value}")
    
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())