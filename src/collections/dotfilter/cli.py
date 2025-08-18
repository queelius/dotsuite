#!/usr/bin/env python3
"""
Command-line interface for dotfilter.

Usage:
    # Filter JSONL by path value
    dotfilter users.jsonl --path role --value admin
    
    # Filter by existence
    dotfilter data.jsonl --exists email
    
    # Complex filtering with Python expression
    dotfilter data.jsonl --expr "d['age'] > 18 and d['status'] == 'active'"
    
    # Combine multiple filters
    dotfilter data.jsonl --path role --value admin --exists email
"""

import sys
import json
import argparse
from typing import Any, List
from .core import filter_docs


def read_jsonl(file_path: str) -> List[Any]:
    """Read JSONL file (one JSON object per line)."""
    documents = []
    if file_path == "-":
        for line in sys.stdin:
            if line.strip():
                documents.append(json.loads(line))
    else:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    documents.append(json.loads(line))
    return documents


def write_jsonl(documents: List[Any], file_path: str = None):
    """Write documents as JSONL."""
    if file_path and file_path != "-":
        f = open(file_path, 'w')
    else:
        f = sys.stdout
    
    try:
        for doc in documents:
            json.dump(doc, f, separators=(',', ':'))
            f.write('\n')
    finally:
        if f != sys.stdout:
            f.close()


def main():
    parser = argparse.ArgumentParser(
        description="Filter JSON document collections"
    )
    parser.add_argument(
        "input",
        help="JSONL file path or '-' for stdin"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: stdout)"
    )
    
    # Filter options
    parser.add_argument(
        "--path", "-p",
        help="Filter by path value (use with --value)"
    )
    parser.add_argument(
        "--value", "-v",
        help="Expected value for --path filter"
    )
    parser.add_argument(
        "--exists", "-e",
        action="append",
        help="Filter where path exists (can be used multiple times)"
    )
    parser.add_argument(
        "--expr", "-x",
        help="Python expression filter (document is 'd')"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["and", "or"],
        default="and",
        help="How to combine multiple filters (default: and)"
    )
    parser.add_argument(
        "--count", "-c",
        action="store_true",
        help="Output count instead of documents"
    )
    parser.add_argument(
        "--invert", "-i",
        action="store_true",
        help="Invert the filter (exclude matching documents)"
    )
    
    args = parser.parse_args()
    
    # Read documents
    documents = read_jsonl(args.input)
    
    # Build filters
    filters = []
    
    if args.path and args.value:
        # Parse value as JSON if possible
        try:
            value = json.loads(args.value)
        except json.JSONDecodeError:
            value = args.value
        
        from truth.dotequals.core import equals
        filters.append(lambda d: equals(d, args.path, value))
    
    if args.exists:
        from truth.dotexists.core import check
        for path in args.exists:
            filters.append(lambda d, p=path: check(d, p))
    
    if args.expr:
        # Create a safe evaluation environment
        def make_expr_filter(expr):
            def filter_fn(d):
                try:
                    # Only allow safe operations
                    return eval(expr, {"__builtins__": {}}, {"d": d})
                except Exception:
                    return False
            return filter_fn
        filters.append(make_expr_filter(args.expr))
    
    # Apply filters
    if filters:
        if len(filters) == 1:
            predicate = filters[0]
        else:
            if args.mode == "and":
                predicate = lambda d: all(f(d) for f in filters)
            else:
                predicate = lambda d: any(f(d) for f in filters)
        
        if args.invert:
            result = filter_docs(documents, lambda d: not predicate(d))
        else:
            result = filter_docs(documents, predicate)
    else:
        result = documents
    
    # Output
    if args.count:
        print(len(result))
    else:
        write_jsonl(result, args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())