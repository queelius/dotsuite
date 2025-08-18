"""
dotequals - Check if a path has a specific value.

Part of the Truth pillar's pattern layer. While dotexists checks if a path exists,
dotequals checks if it exists AND has a specific value. This is pedagogically
positioned between simple existence (dotexists) and complex queries (dotquery).

Following the "steal this code" philosophy, this is intentionally simple.
"""

from typing import Any
from depth.dotget.core import get as dotget


def equals(data: Any, path: str, value: Any) -> bool:
    """
    Check if a path exists and has a specific value.
    
    Args:
        data: The nested data structure
        path: Dot-notation path to check
        value: The expected value
        
    Returns:
        True if the path exists and equals the value, False otherwise
        
    Examples:
        >>> data = {"user": {"name": "Alice", "role": "admin"}}
        >>> equals(data, "user.name", "Alice")
        True
        >>> equals(data, "user.name", "Bob")
        False
        >>> equals(data, "user.email", "alice@example.com")  # path doesn't exist
        False
    """
    try:
        result = dotget(data, path)
        return result == value
    except (KeyError, IndexError, TypeError, AttributeError):
        return False


def not_equals(data: Any, path: str, value: Any) -> bool:
    """
    Check if a path exists and does NOT have a specific value.
    
    Args:
        data: The nested data structure
        path: Dot-notation path to check
        value: The value to compare against
        
    Returns:
        True if the path exists and does not equal the value
        False if the path doesn't exist OR equals the value
        
    Examples:
        >>> data = {"user": {"name": "Alice", "role": "admin"}}
        >>> not_equals(data, "user.name", "Bob")
        True
        >>> not_equals(data, "user.name", "Alice")
        False
        >>> not_equals(data, "user.email", "anything")  # path doesn't exist
        False
    """
    try:
        result = dotget(data, path)
        return result != value
    except (KeyError, IndexError, TypeError, AttributeError):
        return False  # Path doesn't exist, so we can't say it's not equal


def equals_any(data: Any, path: str, *values: Any) -> bool:
    """
    Check if a path exists and equals any of the provided values.
    
    Args:
        data: The nested data structure
        path: Dot-notation path to check
        *values: Possible values to match
        
    Returns:
        True if the path exists and matches any value, False otherwise
        
    Examples:
        >>> data = {"user": {"role": "admin"}}
        >>> equals_any(data, "user.role", "admin", "moderator", "user")
        True
        >>> equals_any(data, "user.role", "guest", "visitor")
        False
    """
    try:
        result = dotget(data, path)
        return result in values
    except (KeyError, IndexError, TypeError, AttributeError):
        return False


# Alias for consistency with other truth tools
check = equals