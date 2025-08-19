# dotexists

**Check if a path exists in nested data**

Part of the Truth pillar, `dotexists` is the most fundamental boolean operation - checking whether a path exists in a data structure.

## Overview

`dotexists` safely navigates through nested dictionaries and lists to determine if a path exists, regardless of the value at that path.

## Basic Usage

```python
from truth.dotexists import check

data = {
    "user": {
        "name": "Alice",
        "email": "alice@example.com",
        "age": None
    }
}

# Check if paths exist
check(data, "user.name")        # True
check(data, "user.email")       # True
check(data, "user.age")         # True (even though value is None)
check(data, "user.phone")       # False
```

## Important: Existence vs Truthiness

`dotexists` returns `True` if the path exists, even if the value is falsy:

```python
data = {
    "count": 0,
    "active": False,
    "name": "",
    "value": None,
    "items": []
}

# All these return True (paths exist)
check(data, "count")    # True (even though 0 is falsy)
check(data, "active")   # True (even though False)
check(data, "name")     # True (even though empty string)
check(data, "value")    # True (even though None)
check(data, "items")    # True (even though empty list)
```

## List Access

Works with list indices:

```python
data = {
    "users": [
        {"name": "Alice"},
        {"name": "Bob"},
        {"name": "Charlie"}
    ]
}

check(data, "users.0")       # True
check(data, "users.2.name")  # True
check(data, "users.3")       # False (out of bounds)
check(data, "users.-1")      # True (negative indexing)
```

## Safe Navigation Pattern

Use `dotexists` for safe navigation before accessing values:

```python
from depth.dotget import get
from truth.dotexists import check

def safe_get(data, path, default=None):
    """Get value if path exists, otherwise return default."""
    if check(data, path):
        return get(data, path)
    return default

# Usage
config = {"database": {"host": "localhost"}}
port = safe_get(config, "database.port", 5432)  # Returns 5432 (default)
```

## Real-World Examples

### Optional Configuration
```python
config = {
    "server": {
        "host": "localhost",
        "port": 8080
        # SSL config is optional
    }
}

# Check for optional settings
if check(config, "server.ssl.enabled"):
    # Configure SSL
    pass
else:
    # Use default (no SSL)
    pass
```

### Feature Detection
```python
user_data = {
    "profile": {
        "name": "Alice",
        "premium_features": {
            "advanced_analytics": True
        }
    }
}

# Check if user has premium features
has_premium = check(user_data, "profile.premium_features")
has_analytics = check(user_data, "profile.premium_features.advanced_analytics")
```

## Mathematical Foundation

`dotexists` implements the membership test (∈) for paths in nested structures:
- Returns `True` ⟺ path ∈ structure
- Returns `False` ⟺ path ∉ structure

## Related Tools

- **[dotget](../depth/dotget.md)** - Extract values from paths
- **[dotequals](dotequals.md)** - Check if path has specific value
- **[dotquery](dotquery.md)** - Complex boolean queries