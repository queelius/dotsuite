# FILE: dotmod/core.py
#
# This file provides the core, immutable modification functions.
# It uses its own internal path traversal logic and does NOT
# depend on dotquery, to ensure semantic clarity and safety.

from copy import deepcopy
from typing import Any, List, Dict, Tuple, Optional

def _find_parent(data: Any, parts: List[str], create_path: bool = False) -> Optional[Tuple[Any, str]]:
    """
    Internal helper to traverse a path and return the parent node and the final key.
    
    Args:
        data: The document to traverse.
        parts: The path, pre-split into a list of segments.
        create_path: If True, creates nested dictionaries for paths that don't exist.
    
    Returns:
        A tuple of (parent, final_key) or None if the path is invalid.
    """
    current = data
    for i, part in enumerate(parts[:-1]):
        try:
            if isinstance(current, list) and part.isdigit():
                current = current[int(part)]
            elif isinstance(current, dict):
                if create_path and part not in current:
                    # Look ahead to see if the next segment is an index, to create a list.
                    is_next_part_digit = parts[i + 1].isdigit()
                    current[part] = [] if is_next_part_digit else {}
                current = current[part]
            else:
                return None # Path is not traversable
        except (KeyError, IndexError):
            return None # Path does not exist
            
    return (current, parts[-1])

def set_(data: Any, path: str, value: Any) -> Any:
    """Immutably sets a value at a specified path, creating the path if it doesn't exist."""
    new_data = deepcopy(data)
    parts = path.split('.')
    if not parts:
        return new_data

    found = _find_parent(new_data, parts, create_path=True)
    if not found:
        # This can happen if the path is invalid, e.g., trying to key into a list.
        return deepcopy(data) 

    parent, key = found
    
    if isinstance(parent, list) and key.isdigit():
        idx = int(key)
        # Pad the list with None if the index is out of bounds
        if idx >= len(parent):
            parent.extend([None] * (idx - len(parent) + 1))
        parent[idx] = value
    elif isinstance(parent, dict):
        parent[key] = value
    
    return new_data

def delete_(data: Any, path: str) -> Any:
    """Immutably deletes a value at a specified path."""
    new_data = deepcopy(data)
    parts = path.split('.')
    if not parts:
        return new_data
        
    found = _find_parent(new_data, parts)
    if not found:
        return new_data # Path or parent not found, return original copy

    parent, key = found
    try:
        if isinstance(parent, list) and key.isdigit():
            del parent[int(key)]
        elif isinstance(parent, dict):
            del parent[key]
    except (KeyError, IndexError):
        # Key doesn't exist at the final step, do nothing.
        pass
        
    return new_data

def _find_target_node(data: Any, path: str) -> Optional[Any]:
    """Internal helper to find the exact node at a given path."""
    current = data
    try:
        for part in path.split('.'):
            if isinstance(current, list) and part.isdigit():
                current = current[int(part)]
            elif isinstance(current, dict):
                current = current[part]
            else:
                return None
    except (KeyError, IndexError, TypeError):
        return None
    return current

def update_(data: Any, path: str, value: Dict) -> Any:
    """Immutably merges a dictionary into a dictionary at the specified path."""
    if not isinstance(value, dict):
        raise TypeError("Value for update_ must be a dictionary.")

    new_data = deepcopy(data)
    target_node = _find_target_node(new_data, path)

    if isinstance(target_node, dict):
        target_node.update(value)
        
    return new_data

def append_(data: Any, path: str, value: Any) -> Any:
    """Immutably appends a value to a list at the specified path."""
    new_data = deepcopy(data)
    target_node = _find_target_node(new_data, path)
        
    if isinstance(target_node, list):
        target_node.append(value)
        
    return new_data
