"""
dotget - Simple, exact addressing for nested data.

A tiny library for accessing nested data structures using dot notation.
No dependencies. No magic. Just simple paths.
"""

from typing import Any
from .path import Path

def get(data: Any, path: str) -> Any:
    """
    Get a value from a nested dictionary-like object using a dot-separated path.
    """
    return Path(path).get(data)