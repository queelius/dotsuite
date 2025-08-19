# dotmod

**Immutable modifications to nested data structures**

Part of the Shape pillar, `dotmod` provides surgical, immutable modifications to nested data structures using dot notation paths.

## Overview

`dotmod` enables you to modify values deep within nested structures without mutating the original data, following functional programming principles.

## Core Operations

### set_ - Set a value at a path

```python
from shape.dotmod import set_

data = {
    "user": {
        "name": "Alice",
        "role": "user"
    }
}

# Create a new structure with modified value
new_data = set_(data, "user.role", "admin")

# Original unchanged
print(data["user"]["role"])      # "user"
print(new_data["user"]["role"])  # "admin"
```

### delete - Remove a path

```python
from shape.dotmod import delete

data = {
    "user": {
        "name": "Alice",
        "email": "alice@example.com",
        "temp_token": "xyz123"
    }
}

# Remove temporary token
clean_data = delete(data, "user.temp_token")
# {"user": {"name": "Alice", "email": "alice@example.com"}}
```

### update - Apply a function to a value

```python
from shape.dotmod import update

data = {
    "product": {
        "name": "Widget",
        "price": 10.00
    }
}

# Apply discount
discounted = update(data, "product.price", lambda p: p * 0.9)
# {"product": {"name": "Widget", "price": 9.00}}
```

## Creating Nested Structures

`dotmod` automatically creates intermediate structures as needed:

```python
from shape.dotmod import set_

data = {}

# Creates nested structure
result = set_(data, "user.profile.settings.theme", "dark")
# {
#     "user": {
#         "profile": {
#             "settings": {
#                 "theme": "dark"
#             }
#         }
#     }
# }
```

## Working with Lists

Modify list elements by index:

```python
data = {
    "items": [
        {"id": 1, "status": "pending"},
        {"id": 2, "status": "pending"},
        {"id": 3, "status": "pending"}
    ]
}

# Update second item's status
result = set_(data, "items.1.status", "completed")

# Extend lists automatically
result = set_(data, "items.3.status", "new")
# Automatically extends the list
```

## Immutability Guarantees

All operations return new structures with shared, unchanged parts:

```python
original = {
    "a": {"x": 1, "y": 2},
    "b": {"x": 3, "y": 4}
}

# Modify a.x
modified = set_(original, "a.x", 10)

# Only 'a' is cloned, 'b' is shared
assert original["b"] is modified["b"]  # True (shared)
assert original["a"] is not modified["a"]  # True (cloned)
```

## Real-World Examples

### Configuration Updates
```python
config = {
    "server": {
        "host": "localhost",
        "port": 8080,
        "ssl": False
    }
}

# Update for production
prod_config = (
    set_(config, "server.host", "api.example.com")
    |> set_("server.port", 443)
    |> set_("server.ssl", True)
)
```

### State Management
```python
app_state = {
    "user": {"id": 1, "name": "Alice"},
    "ui": {"theme": "light", "sidebar": True}
}

# User action: toggle theme
new_state = update(app_state, "ui.theme", 
                  lambda t: "dark" if t == "light" else "light")
```

### Data Sanitization
```python
user_data = {
    "profile": {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secret123",  # Don't send to client!
        "ssn": "123-45-6789"      # Sensitive!
    }
}

# Remove sensitive fields
public_data = (
    delete(user_data, "profile.password")
    |> delete("profile.ssn")
)
```

## Integration with Other Tools

```python
from depth.dotget import get
from shape.dotmod import set_
from truth.dotexists import check

def safe_increment(data, path, amount=1):
    """Safely increment a numeric value."""
    if check(data, path):
        current = get(data, path) or 0
        return set_(data, path, current + amount)
    return set_(data, path, amount)
```

## Mathematical Foundation

`dotmod` implements a functional update operation that preserves referential transparency:
- **Immutability**: f(data) produces new data, original unchanged
- **Path-based addressing**: Updates are localized to paths
- **Structural sharing**: Unchanged parts share memory

## Related Tools

- **[dotbatch](dotbatch.md)** - Atomic batch operations
- **[dotpipe](dotpipe.md)** - Chain transformations
- **[dotget](../depth/dotget.md)** - Read values from paths