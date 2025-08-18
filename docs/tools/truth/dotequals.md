# dotequals

> Check if a path has a specific value - Truth pillar's pattern layer

## Overview

`dotequals` bridges the gap between simple existence checks (`dotexists`) and complex boolean queries (`dotquery`). It answers the question: "Does this path exist AND have this specific value?"

Part of the Truth pillar's pattern layer, it's pedagogically positioned to introduce value checking after users master path existence.

## Installation

```bash
# As part of dotsuite
pip install dotsuite

# Or from source
cd src/truth/dotequals
pip install -e .
```

## Core Functions

### `equals(data, path, value)`

Check if a path exists and has a specific value.

```python
from truth.dotequals.core import equals

data = {
    "user": {
        "name": "Alice",
        "role": "admin",
        "active": True
    }
}

# Check exact values
equals(data, "user.name", "Alice")     # True
equals(data, "user.name", "Bob")       # False
equals(data, "user.role", "admin")     # True
equals(data, "user.active", True)      # True

# Missing paths return False
equals(data, "user.email", "alice@example.com")  # False
```

### `not_equals(data, path, value)`

Check if a path exists and does NOT have a specific value.

```python
from truth.dotequals.core import not_equals

data = {"status": "active", "count": 42}

not_equals(data, "status", "inactive")  # True
not_equals(data, "status", "active")    # False
not_equals(data, "count", 0)            # True

# Note: Missing paths return True (None != value)
not_equals(data, "missing", "anything")  # True
not_equals(data, "missing", None)        # False
```

### `equals_any(data, path, *values)`

Check if a path equals any of the provided values.

```python
from truth.dotequals.core import equals_any

data = {"user": {"role": "moderator"}}

# Check against multiple possibilities
equals_any(data, "user.role", "admin", "moderator", "superuser")  # True
equals_any(data, "user.role", "user", "guest")                   # False
```

## Command Line Usage

```bash
# Basic equality check
dotequals data.json user.role admin
echo $?  # 0 if true, 1 if false

# Check if NOT equal
dotequals data.json status inactive --not

# Check if equals any of several values
dotequals data.json user.role admin --any moderator superuser

# Verbose output
dotequals data.json user.active true --verbose
# ✓ Path 'user.active' equals true
```

Exit codes:
- `0` - Condition is true
- `1` - Condition is false

## Common Use Cases

### 1. Configuration Validation

```python
config = {
    "environment": "production",
    "debug": False,
    "database": {
        "driver": "postgresql",
        "host": "localhost"
    }
}

# Validate critical settings
if equals(config, "environment", "production"):
    assert equals(config, "debug", False), "Debug must be off in production!"
    assert equals_any(config, "database.driver", "postgresql", "mysql")
```

### 2. User Authorization

```python
user = {
    "id": 123,
    "role": "admin",
    "permissions": ["read", "write", "delete"],
    "active": True
}

def can_delete(user_data):
    return (
        equals(user_data, "active", True) and
        equals_any(user_data, "role", "admin", "superuser")
    )
```

### 3. State Machine Validation

```python
order = {
    "id": "ORD-123",
    "status": "pending",
    "payment": {
        "status": "authorized"
    }
}

# Check if order can be shipped
can_ship = (
    equals(order, "status", "pending") and
    equals(order, "payment.status", "authorized")
)
```

### 4. Shell Script Conditions

```bash
#!/bin/bash

# Check environment before deployment
if dotequals config.json environment production; then
    if ! dotequals config.json debug false; then
        echo "ERROR: Debug mode is on in production!"
        exit 1
    fi
fi

# Check service status
if dotequals status.json service.state running; then
    echo "Service is running"
else
    echo "Service is not running"
    systemctl start myservice
fi
```

## Design Decisions

### Missing Paths

When a path doesn't exist:
- `equals` returns `False` (can't equal a value if it doesn't exist)
- `not_equals` returns `True` (None != any non-None value)
- `equals_any` returns `False` (can't match any value if it doesn't exist)

This behavior is consistent with `dotget` returning `None` for missing paths.

### Type Sensitivity

Comparisons are type-sensitive:
```python
data = {"count": 42}
equals(data, "count", 42)    # True
equals(data, "count", "42")  # False - different types
```

## Philosophy

`dotequals` follows the "steal this code" philosophy. It's essentially:

```python
def equals(data, path, value):
    return get(data, path) == value
```

But with proper handling of missing paths and consistent behavior across the ecosystem.

## Comparison with Other Truth Tools

| Tool | Question | Example |
|------|----------|---------|
| `dotexists` | Does path exist? | `check(data, "user.email")` |
| `dotequals` | Does path have value? | `equals(data, "status", "active")` |
| `dotany` | Does any item match? | `any_match(data, "users.*.role", "admin")` |
| `dotall` | Do all items match? | `all_match(data, "users.*.active", True)` |
| `dotquery` | Complex boolean logic | `Query("age > 18 and role == admin")` |

## See Also

- [`dotexists`](../truth/dotexists.md) - Check path existence
- [`dotquery`](../truth/dotquery.md) - Complex boolean queries
- [`dotany`](../truth/dotany.md) - Existential quantifier
- [`dotall`](../truth/dotall.md) - Universal quantifier