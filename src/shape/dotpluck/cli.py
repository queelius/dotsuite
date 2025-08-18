#!/usr/bin/env python3
"""
Command-line interface for dotpluck.

Usage:
    dotpluck data.json path1 path2 path3
    echo '{"a": 1, "b": 2}' | dotpluck - a b
"""

import sys
import json
import argparse
from .core import pluck


def main():
    parser = argparse.ArgumentParser(
        description="Extract values from JSON data using dot notation paths"
    )
    parser.add_argument(
        "input",
        help="JSON file path or '-' for stdin"
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Dot notation paths to extract"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON array (default: one value per line)"
    )
    
    args = parser.parse_args()
    
    # Read input
    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        with open(args.input, "r") as f:
            data = json.load(f)
    
    # Extract values
    values = pluck(data, *args.paths)
    
    # Output
    if args.json:
        print(json.dumps(values))
    else:
        for value in values:
            if value is None:
                print("null")
            elif isinstance(value, str):
                print(value)
            else:
                print(json.dumps(value))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())