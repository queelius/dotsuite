# dotget

**Simple, exact addressing for nested data**

The foundational tool of the Depth pillar, `dotget` safely extracts values from nested data structures using dot notation paths.

## Overview

`dotget` is the tool that started it all - a simple function to safely navigate nested dictionaries and lists without worrying about KeyErrors or IndexErrors.

## Basic Usage

```python
from depth.dotget import get

data = {
    "user": {
        "name": "Alice",
        "contacts": {
            "email": "alice@example.com",
            "phone": "+1-555-0100"
        }
    }
}

# Get nested values
name = get(data, "user.name")                    # "Alice"
email = get(data, "user.contacts.email")         # "alice@example.com"
missing = get(data, "user.contacts.fax")         # None
```

## Safe Navigation

Unlike direct dictionary access, `dotget` never raises exceptions:

```python
# This would raise KeyError:
# value = data["user"]["settings"]["theme"]

# This returns None safely:
value = get(data, "user.settings.theme")  # None
```

## List Access

Navigate through lists using numeric indices:

```python
data = {
    "users": [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
}

# Access by index
first_user = get(data, "users.0.name")      # "Alice"
second_age = get(data, "users.1.age")       # 25

# Negative indices work too
last_user = get(data, "users.-1.name")      # "Charlie"

# Out of bounds returns None
missing = get(data, "users.10.name")        # None
```

## Mixed Structures

Navigate seamlessly through mixed dictionaries and lists:

```python
data = {
    "company": {
        "departments": [
            {
                "name": "Engineering",
                "teams": [
                    {"name": "Backend", "size": 5},
                    {"name": "Frontend", "size": 3}
                ]
            }
        ]
    }
}

# Deep navigation
team_size = get(data, "company.departments.0.teams.1.size")  # 3
```

## Real-World Examples

### API Response Parsing
```python
response = {
    "data": {
        "user": {
            "id": 123,
            "profile": {
                "firstName": "Alice",
                "lastName": "Smith"
            }
        }
    },
    "meta": {
        "timestamp": "2024-01-01T12:00:00Z"
    }
}

user_id = get(response, "data.user.id")           # 123
full_name = f"{get(response, 'data.user.profile.firstName')} {get(response, 'data.user.profile.lastName')}"
```

### Configuration Access
```python
config = {
    "database": {
        "primary": {
            "host": "db1.example.com",
            "port": 5432
        }
    }
}

# Safe configuration access with defaults
db_host = get(config, "database.primary.host") or "localhost"
db_port = get(config, "database.primary.port") or 5432
db_user = get(config, "database.primary.user") or "postgres"
```

### JSON Data Processing
```python
import json

# Load JSON data
with open("data.json") as f:
    data = json.load(f)

# Safely extract nested values
for i in range(100):  # Don't know how many items
    name = get(data, f"items.{i}.name")
    if name is None:
        break  # No more items
    print(name)
```

## Design Philosophy

`dotget` embodies the principle of **graceful degradation**:
- Never raises exceptions for missing paths
- Returns `None` for any navigation failure
- Simple, predictable behavior
- Zero dependencies

## Performance

`dotget` is optimized for simplicity and safety, not speed:
- O(n) where n is the depth of the path
- Minimal memory overhead
- No caching or memoization

For performance-critical applications with known schemas, direct dictionary access is faster.

## Related Tools

- **[dotstar](../depth/dotstar.md)** - Pattern matching with wildcards
- **[dotexists](../truth/dotexists.md)** - Check if path exists
- **[dotmod](../shape/dotmod.md)** - Modify values at paths