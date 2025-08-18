from typing import Any, List
from depth.dotget.core import get

def any_match(collection: List[Any], path: str, value: Any) -> bool:
    """
    Checks if any document in the collection has the specified value at the given path.
    
    This is the existential quantifier for collections - returns True if at least one
    document in the collection has the specified value at the path.
    
    Args:
        collection: List of documents to check
        path: Dot notation path to check in each document
        value: Value to match against
        
    Returns:
        True if any document has the value at the path, False otherwise
        
    Examples:
        >>> users = [{"name": "Alice", "role": "admin"}, {"name": "Bob", "role": "user"}]
        >>> any_match(users, "role", "admin")
        True
        >>> any_match(users, "role", "moderator")
        False
    """
    if not collection:
        return False
    
    for doc in collection:
        try:
            if get(doc, path) == value:
                return True
        except (KeyError, IndexError, TypeError, AttributeError):
            # Path doesn't exist in this document, continue to next
            continue
    
    return False
