from typing import Any
import dotpath

def check(data: Any, path: str, equals: Any) -> bool:
    """
    Checks if any value at a given path equals the specified value.
    """
    values = dotpath.find_all(data, path)
    # If find_all returns an empty list, any() will be False.
    return any(v == equals for v in values)
