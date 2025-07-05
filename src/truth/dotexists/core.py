from typing import Any

def check(data: Any, path: str) -> bool:
    """
    Check if a path exists in a nested dictionary-like object.
    """
    parts = path.split('.')
    for part in parts:
        if isinstance(data, dict):
            if part not in data:
                return False
            data = data[part]
        elif isinstance(data, list):
            try:
                part_index = int(part)
                if not (-len(data) <= part_index < len(data)):
                    return False
                data = data[part_index]
            except (ValueError, IndexError):
                return False
        else:
            # The path continues, but we have a non-container type
            return False
    return True
