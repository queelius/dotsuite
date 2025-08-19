# dotstar

**Pattern matching with wildcards for nested data**

Part of the Depth pillar, `dotstar` extends `dotget` with wildcard support, enabling you to search for multiple values matching a pattern.

## Overview

While `dotget` retrieves a single value at an exact path, `dotstar` can find all values matching a pattern with wildcards, making it perfect for data exploration and bulk operations.

## Wildcard Patterns

The `*` wildcard matches any key or index:

```python
from depth.dotstar import search

data = {
    "users": [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]
}

# Get all user names
names = search(data, "users.*.name")
# ["Alice", "Bob", "Charlie"]

# Get all ages
ages = search(data, "users.*.age")  
# [30, 25, 35]
```

## Multiple Wildcards

Use multiple wildcards to search deeper:

```python
data = {
    "departments": {
        "engineering": {
            "teams": {
                "backend": {"members": 5},
                "frontend": {"members": 3}
            }
        },
        "sales": {
            "teams": {
                "inbound": {"members": 4},
                "outbound": {"members": 6}
            }
        }
    }
}

# Get all team member counts
counts = search(data, "departments.*.teams.*.members")
# [5, 3, 4, 6]
```

## Dictionary Wildcards

Wildcards work with dictionary keys:

```python
data = {
    "server1": {"status": "active", "cpu": 45},
    "server2": {"status": "active", "cpu": 67},
    "server3": {"status": "inactive", "cpu": 12}
}

# Get all server statuses
statuses = search(data, "*.status")
# ["active", "active", "inactive"]

# Get all CPU values
cpus = search(data, "*.cpu")
# [45, 67, 12]
```

## Finding Paths with find_all

Get both paths and values:

```python
from depth.dotstar import find_all

data = {
    "users": [
        {"name": "Alice", "role": "admin"},
        {"name": "Bob", "role": "user"}
    ]
}

# Get paths and values
results = find_all(data, "users.*.role")
# [
#   ("users.0.role", "admin"),
#   ("users.1.role", "user")
# ]

# Useful for updates
for path, value in results:
    if value == "admin":
        print(f"Admin found at: {path}")
```

## Pattern Class

Build reusable patterns:

```python
from depth.dotstar import Pattern

# Create reusable patterns
user_emails = Pattern("users.*.email")
user_names = Pattern("users.*.name")

# Apply to different datasets
emails1 = user_emails.search(dataset1)
emails2 = user_emails.search(dataset2)

# Compose patterns
admins = Pattern("users.*[role=admin]")  # Future feature
```

## Real-World Examples

### Extract All Email Addresses

```python
organization = {
    "departments": [
        {
            "name": "Engineering",
            "employees": [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"}
            ]
        },
        {
            "name": "Sales",
            "employees": [
                {"name": "Charlie", "email": "charlie@example.com"}
            ]
        }
    ]
}

# Get all employee emails
emails = search(organization, "departments.*.employees.*.email")
# ["alice@example.com", "bob@example.com", "charlie@example.com"]
```

### Aggregate Metrics

```python
metrics = {
    "services": {
        "api": {
            "endpoints": {
                "users": {"requests": 1000, "errors": 5},
                "posts": {"requests": 500, "errors": 2}
            }
        },
        "web": {
            "endpoints": {
                "home": {"requests": 5000, "errors": 10},
                "about": {"requests": 200, "errors": 0}
            }
        }
    }
}

# Get all request counts
total_requests = sum(search(metrics, "services.*.endpoints.*.requests"))
# 6700

# Get all error counts
total_errors = sum(search(metrics, "services.*.endpoints.*.errors"))
# 17
```

### Find Configuration Values

```python
config = {
    "environments": {
        "dev": {
            "database": {"host": "localhost", "port": 5432},
            "cache": {"host": "localhost", "port": 6379}
        },
        "prod": {
            "database": {"host": "db.prod.com", "port": 5432},
            "cache": {"host": "cache.prod.com", "port": 6379}
        }
    }
}

# Find all database hosts
db_hosts = search(config, "environments.*.database.host")
# ["localhost", "db.prod.com"]

# Find all ports
all_ports = search(config, "environments.*.*.port")
# [5432, 6379, 5432, 6379]
```

### Data Validation

```python
# Check if all required fields exist
products = [
    {"id": 1, "name": "Widget", "price": 9.99},
    {"id": 2, "name": "Gadget", "price": 19.99},
    {"id": 3, "name": "Gizmo"}  # Missing price!
]

prices = search({"products": products}, "products.*.price")
if len(prices) != len(products):
    print("Warning: Some products missing prices!")
```

## Performance Considerations

- **Linear search**: O(n) where n is total number of nodes
- **No indexing**: Each search traverses the entire structure
- **Memory efficient**: Returns list of values, not full paths
- **Use find_all**: When you need paths for later updates

## Comparison with dotget

| Feature | dotget | dotstar |
|---------|--------|---------|
| Purpose | Single value | Multiple values |
| Wildcards | No | Yes (*) |
| Return type | Single value or None | List of values |
| Performance | O(depth) | O(nodes) |
| Use case | Known paths | Pattern search |

## Advanced Patterns (Future)

Planned enhancements:
- `**` for recursive descent
- `[n:m]` for slice notation
- `[?filter]` for inline filtering
- `{key1,key2}` for multiple specific keys

## Related Tools

- **[dotget](dotget.md)** - Simple exact path access
- **[dotselect](dotselect.md)** - Advanced selection with predicates
- **[dotpath](dotpath.md)** - Underlying path engine
- **[dotmod](../shape/dotmod.md)** - Modify values found by patterns