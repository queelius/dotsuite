import json
from typing import Any, Dict, Iterator, List, Union

def left_join(left_collection: List[Dict], right_collection: List[Dict], 
              left_on: str, right_on: str) -> Iterator[Dict]:
    """
    Perform a left join on two collections.
    
    Returns all items from the left collection, with matching data from the right
    collection merged in. If multiple right items match, all combinations are returned.
    If no right items match, the left item is returned unchanged.
    
    Args:
        left_collection: The left collection
        right_collection: The right collection  
        left_on: Key in left collection to join on
        right_on: Key in right collection to join on
        
    Yields:
        Merged dictionaries with all left items preserved
    """
    # Build index on right collection for efficient lookups
    # Store all matching items in a list to handle multiple matches
    right_index = {}
    for right_item in right_collection:
        key = right_item.get(right_on)
        if key is not None:
            right_index.setdefault(key, []).append(right_item)
    
    for left_item in left_collection:
        left_key = left_item.get(left_on)
        matching_right_items = right_index.get(left_key, [])
        
        if matching_right_items:
            # Yield a result for each matching right item
            for right_item in matching_right_items:
                merged = left_item.copy()
                # Add fields from right, avoiding overwrite of join key
                for key, value in right_item.items():
                    if key != right_on or key not in merged:
                        merged[key] = value
                yield merged
        else:
            # No matches - yield left item unchanged
            yield left_item.copy()

def project(collection: Iterator[Dict], fields: List[str]) -> Iterator[Dict]:
    """
    Project specific fields from each item in a collection.
    
    Args:
        collection: Input collection
        fields: List of field names to keep
        
    Yields:
        Dictionaries containing only the specified fields
    """
    for item in collection:
        yield {field: item.get(field) for field in fields}

def union(left_collection: Iterator[Dict], right_collection: Iterator[Dict]) -> Iterator[Dict]:
    """
    Union of two collections (concatenation).
    
    Args:
        left_collection: First collection
        right_collection: Second collection
        
    Yields:
        All items from both collections
    """
    yield from left_collection
    yield from right_collection

def inner_join(left_collection: List[Dict], right_collection: List[Dict],
               left_on: str, right_on: str) -> Iterator[Dict]:
    """
    Perform an inner join on two collections.
    
    Returns only items where there is a match between left and right collections.
    If multiple matches exist, all combinations are returned.
    
    Args:
        left_collection: The left collection
        right_collection: The right collection
        left_on: Key in left collection to join on
        right_on: Key in right collection to join on
        
    Yields:
        Merged dictionaries for matching items only
    """
    # Build index on right collection
    right_index = {}
    for right_item in right_collection:
        key = right_item.get(right_on)
        if key is not None:
            right_index.setdefault(key, []).append(right_item)
    
    for left_item in left_collection:
        left_key = left_item.get(left_on)
        matching_right_items = right_index.get(left_key, [])
        
        # Only yield if there are matches (inner join)
        for right_item in matching_right_items:
            merged = left_item.copy()
            for key, value in right_item.items():
                if key != right_on or key not in merged:
                    merged[key] = value
            yield merged

def set_difference(left_collection: List[Dict], right_collection: List[Dict]) -> Iterator[Dict]:
    """
    Set difference - items in left but not in right.
    
    Args:
        left_collection: Collection to subtract from
        right_collection: Collection to subtract
        
    Yields:
        Items that exist in left but not in right
    """
    right_set = {json.dumps(item, sort_keys=True) for item in right_collection}
    for item in left_collection:
        if json.dumps(item, sort_keys=True) not in right_set:
            yield item
