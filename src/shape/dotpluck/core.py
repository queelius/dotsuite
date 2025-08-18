"""
dotpluck - Project data out of documents into new shapes.

The primitive for the Shape pillar. Unlike dotget which navigates to values,
dotpluck RESHAPES data by projecting selected parts into new structures.
It's not a transform (doesn't return documents), but a projection to simpler forms.

This is the "Hello World" of reshaping - extracting subsets of data into new shapes.
"""

from typing import Any
from depth.dotget.core import get as dotget


def pluck(data: Any, shape: dict) -> dict:
    """
    Project data into a new shape by extracting and restructuring selected paths.
    
    This is the Shape pillar's primitive - it's about RESHAPING, not just getting values.
    It projects parts of a document into a completely new structure.
    
    Args:
        data: The source document
        shape: A dictionary defining the new shape, where values are paths to pluck
        
    Returns:
        New dictionary with the specified shape
        
    Examples:
        >>> data = {"user": {"firstName": "Alice", "lastName": "Smith", "age": 30}}
        >>> pluck(data, {"name": "user.firstName", "years": "user.age"})
        {'name': 'Alice', 'years': 30}
        
        >>> # Nested reshaping
        >>> pluck(data, {"person": {"first": "user.firstName", "last": "user.lastName"}})
        {'person': {'first': 'Alice', 'last': 'Smith'}}
    """
    if not isinstance(shape, dict):
        return shape
    
    result = {}
    for key, value in shape.items():
        if isinstance(value, dict):
            # Recursive reshaping for nested structures
            result[key] = pluck(data, value)
        elif isinstance(value, str):
            # It's a path - extract the value
            try:
                result[key] = dotget(data, value)
            except (KeyError, IndexError, TypeError, AttributeError):
                result[key] = None
        else:
            # Static value
            result[key] = value
    return result


def pluck_simple(data: Any, **paths: str) -> dict:
    """
    Simple projection - convenience wrapper for flat reshaping.
    
    Args:
        data: The source document
        **paths: Mapping of output keys to input paths
        
    Returns:
        New flat dictionary
        
    Examples:
        >>> data = {"user": {"firstName": "Alice", "years": 30}}
        >>> pluck_simple(data, name="user.firstName", age="user.years")
        {'name': 'Alice', 'age': 30}
    """
    return pluck(data, paths)


def pluck_subset(data: Any, path: str, *keys: str) -> dict:
    """
    Project a subset of an object's fields.
    
    Useful for extracting only certain fields from a nested object.
    
    Args:
        data: The source document
        path: Path to the object to subset
        *keys: Keys to include in the projection
        
    Returns:
        Dictionary with only the specified keys
        
    Examples:
        >>> data = {"user": {"id": 1, "name": "Alice", "password": "secret", "email": "alice@example.com"}}
        >>> pluck_subset(data, "user", "id", "name", "email")  # Exclude password
        {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
    """
    try:
        source_obj = dotget(data, path)
    except (KeyError, IndexError, TypeError, AttributeError):
        return {}
    
    if not isinstance(source_obj, dict):
        return {}
    
    return {key: source_obj.get(key) for key in keys if key in source_obj}


def pluck_list(data: Any, *paths: str) -> list:
    """
    Project values into a simple list (no keys).
    
    This is closer to the original "multiple dotget" idea but explicitly
    returns a list for when you just need values, not structure.
    
    Args:
        data: The source document
        *paths: Paths to extract
        
    Returns:
        List of values
        
    Examples:
        >>> data = {"user": {"name": "Alice", "age": 30}}
        >>> pluck_list(data, "user.name", "user.age")
        ['Alice', 30]
    """
    result = []
    for path in paths:
        try:
            result.append(dotget(data, path))
        except (KeyError, IndexError, TypeError, AttributeError):
            result.append(None)
    return result