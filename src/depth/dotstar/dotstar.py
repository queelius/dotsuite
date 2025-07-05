"""
dotstar - Pattern matching for dotget paths.

Extends dotget with wildcard support for matching multiple values.

Basic usage:
    >>> from dotstar import search
    >>> data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
    >>> search(data, "users.*.name")
    ['Alice', 'Bob']
"""

def search(data, pattern):
    """
    Search for all values matching a pattern with wildcards.

    Args:
        data: The nested data structure
        pattern: Dot-path pattern with wildcards (* matches any key/index)

    Returns:
        List of all matching values (empty list if no matches)

    Examples:
        >>> data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        >>> search(data, "users.*.name")
        ['Alice', 'Bob']

        >>> data = {"a": {"x": 1, "y": 2}, "b": {"x": 3, "y": 4}}
        >>> search(data, "*.x")
        [1, 3]
    """
    if isinstance(pattern, Pattern):
        pattern = str(pattern)

    results = []
    _search_recursive(data, pattern.split('.'), results)
    return results


def find_all(data, pattern):
    """
    Find all paths and values matching a pattern.

    Args:
        data: The nested data structure
        pattern: Dot-path pattern with wildcards

    Returns:
        List of (path, value) tuples for all matches

    Examples:
        >>> data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        >>> find_all(data, "users.*.name")
        [('users.0.name', 'Alice'), ('users.1.name', 'Bob')]
    """
    if isinstance(pattern, Pattern):
        pattern = str(pattern)

    results = []
    _find_recursive(data, pattern.split('.'), [], results)
    return results


def _search_recursive(data, segments, results):
    """Recursively search for values matching pattern segments."""
    if not segments:
        results.append(data)
        return

    segment = segments[0]
    remaining = segments[1:]

    if segment == '*':
        # Wildcard: explore all branches
        if isinstance(data, dict):
            for value in data.values():
                _search_recursive(value, remaining, results)
        elif isinstance(data, list):
            for item in data:
                _search_recursive(item, remaining, results)
    else:
        # Specific key/index
        try:
            if isinstance(data, list) and segment.isdigit():
                next_data = data[int(segment)]
            elif isinstance(data, dict):
                next_data = data[segment]
            else:
                return
            _search_recursive(next_data, remaining, results)
        except (KeyError, IndexError, TypeError):
            return


def _find_recursive(data, segments, current_path, results):
    """Recursively find all paths matching pattern segments."""
    if not segments:
        path_str = '.'.join(current_path)
        results.append((path_str, data))
        return

    segment = segments[0]
    remaining = segments[1:]

    if segment == '*':
        # Wildcard: explore all branches
        if isinstance(data, dict):
            for key, value in data.items():
                _find_recursive(value, remaining, current_path + [key], results)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                _find_recursive(item, remaining, current_path + [str(i)], results)
    else:
        # Specific key/index
        try:
            if isinstance(data, list) and segment.isdigit():
                next_data = data[int(segment)]
            elif isinstance(data, dict):
                next_data = data[segment]
            else:
                return
            _find_recursive(next_data, remaining, current_path + [segment], results)
        except (KeyError, IndexError, TypeError):
            return


class Pattern:
    """
    A pattern object for wildcard paths.

    Examples:
        >>> p = Pattern("users.*.email")
        >>> emails = p.search(data)

        >>> # Pattern composition
        >>> users = Pattern("users.*")
        >>> user_emails = users / "email"
    """

    def __init__(self, pattern=""):
        """Create a pattern from string."""
        self.pattern = pattern

    def __str__(self):
        """String representation."""
        return self.pattern

    def __repr__(self):
        """Developer representation."""
        return f"Pattern({self.pattern!r})"

    def __truediv__(self, other):
        """Join patterns using / operator."""
        if isinstance(other, Pattern):
            other = str(other)

        if not self.pattern:
            return Pattern(other)
        if not other:
            return Pattern(self.pattern)

        return Pattern(f"{self.pattern}.{other}")

    def search(self, data):
        """Search for all values matching this pattern."""
        return search(data, self.pattern)

    def find_all(self, data):
        """Find all paths and values matching this pattern."""
        return find_all(data, self.pattern)
