# dotpluck

> Project data into new shapes - the Shape pillar's primitive

## Overview

`dotpluck` is the foundational tool in the Shape pillar. Unlike `dotget` which navigates to values, `dotpluck` RESHAPES data by projecting selected parts into new structures. It's not about extraction, but about creating new shapes from existing data - the "Hello World" of data transformation.

## Installation

```bash
# As part of dotsuite
pip install dotsuite

# Or from source
cd src/shape/dotpluck
pip install -e .
```

## Core Functions

### `pluck(data, shape)`

Project data into a new shape by extracting and restructuring selected paths.

```python
from shape.dotpluck.core import pluck

data = {
    "user": {
        "firstName": "Alice",
        "lastName": "Smith",
        "age": 30,
        "email": "alice@example.com"
    },
    "settings": {
        "theme": "dark"
    }
}

# Create a new shape
result = pluck(data, {
    "name": "user.firstName",
    "years": "user.age",
    "contact": "user.email"
})
# Returns: {'name': 'Alice', 'years': 30, 'contact': 'alice@example.com'}

# Nested reshaping
result = pluck(data, {
    "person": {
        "first": "user.firstName",
        "last": "user.lastName"
    },
    "preferences": {
        "display": "settings.theme"
    }
})
# Returns: {'person': {'first': 'Alice', 'last': 'Smith'}, 'preferences': {'display': 'dark'}}
```

### `pluck_simple(data, **paths)`

Simple projection - convenience wrapper for flat reshaping.

```python
from shape.dotpluck.core import pluck_simple

data = {
    "customer": {
        "firstName": "Alice",
        "lastName": "Smith",
        "yearsOld": 30
    }
}

# Create new flat structure
result = pluck_simple(
    data,
    name="customer.firstName",
    surname="customer.lastName",
    age="customer.yearsOld"
)
# Returns: {'name': 'Alice', 'surname': 'Smith', 'age': 30}
```

### `pluck_subset(data, path, *keys)`

Project a subset of an object's fields.

```python
from shape.dotpluck.core import pluck_subset

data = {
    "user": {
        "id": 123,
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secret",
        "created_at": "2024-01-01"
    }
}

# Extract only public fields
public_info = pluck_subset(data, "user", "id", "name", "email")
# Returns: {'id': 123, 'name': 'Alice', 'email': 'alice@example.com'}
```

### `pluck_list(data, *paths)`

Project values into a simple list (no keys).

```python
from shape.dotpluck.core import pluck_list

data = {"user": {"name": "Alice", "age": 30}}

# When you just need values, not structure
values = pluck_list(data, "user.name", "user.age", "user.role")
# Returns: ['Alice', 30, None]
```

## Command Line Usage

```bash
# Reshape data with a shape specification
echo '{"user": {"name": "Alice", "age": 30}}' | dotpluck - '{"name": "user.name", "years": "user.age"}'

# Extract specific fields as a list
dotpluck data.json --list user.name user.email user.role

# Project a subset of fields
dotpluck data.json --subset user id name email
```

## Common Use Cases

### 1. API Response Reshaping

Transform API responses into the shape your application needs:

```python
api_response = {
    "data": {
        "user": {
            "id": 123,
            "name": "Alice",
            "email": "alice@example.com",
            "internal_id": "xyz789",
            "created_at": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-15T10:30:00Z",
            "_metadata": {...}
        },
        "subscription": {
            "plan": "premium",
            "expires": "2025-01-01"
        }
    }
}

# Reshape for your UI component
ui_data = pluck(api_response, {
    "user": {
        "id": "data.user.id",
        "name": "data.user.name",
        "email": "data.user.email"
    },
    "subscription": "data.subscription.plan",
    "isPremium": True  # Static value
})
# Returns: structured data ready for your UI
```

### 2. Configuration Reshaping

Create deployment-specific configurations:

```python
full_config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp",
        "pool_size": 10
    },
    "cache": {
        "host": "localhost",
        "port": 6379
    },
    "logging": {
        "level": "debug",
        "file": "/var/log/app.log"
    }
}

# Create environment-specific config
production_config = pluck(full_config, {
    "connections": {
        "db": "database.host",
        "cache": "cache.host"
    },
    "database": {
        "name": "database.name",
        "pool": "database.pool_size"
    },
    "log_level": "warning"  # Override for production
})
```

### 3. Data Schema Migration

Migrate between different data schemas:

```python
old_format = {
    "customer_info": {
        "personal": {
            "first_name": "Alice",
            "last_name": "Smith"
        },
        "contact": {
            "email_address": "alice@example.com",
            "phone": "+1234567890"
        },
        "account": {
            "created": "2020-01-01",
            "type": "premium"
        }
    }
}

# Migrate to new nested schema
new_format = pluck(old_format, {
    "profile": {
        "name": {
            "first": "customer_info.personal.first_name",
            "last": "customer_info.personal.last_name"
        },
        "contactMethods": {
            "primary": "customer_info.contact.email_address",
            "phone": "customer_info.contact.phone"
        }
    },
    "metadata": {
        "accountType": "customer_info.account.type",
        "customerSince": "customer_info.account.created"
    }
})
```

## Philosophy

`dotpluck` represents the Shape pillar's core concept: reshaping data into new forms. While it uses `dotget` internally, its purpose is fundamentally different - it's about projection and transformation, not just extraction.

The implementation is pedagogically simple but conceptually powerful:

```python
def pluck(data, shape):
    """Project data into a new shape."""
    if isinstance(shape, dict):
        return {k: pluck(data, v) for k, v in shape.items()}
    elif isinstance(shape, str):
        return get(data, shape)  # Path to extract
    else:
        return shape  # Static value
```

This recursive structure allows arbitrary reshaping while maintaining simplicity.

## Comparison with Other Tools

| Tool | Purpose | Philosophy | Returns |
|------|---------|------------|---------|
| `dotget` | Navigate to single value | Depth pillar - finding data | Single value |
| `dotpluck` | Reshape/project data | Shape pillar - transformation | New structure |
| `dotstar` | Search with patterns | Depth pillar - pattern matching | List of matches |
| `dotmod` | Modify in place | Shape pillar - surgical edits | Modified document |

The key distinction: `dotget` and `dotstar` are about FINDING data (Depth pillar), while `dotpluck` and `dotmod` are about RESHAPING data (Shape pillar).

## See Also

- [`dotget`](../depth/dotget.md) - Simple single value extraction
- [`dotmod`](../shape/dotmod.md) - Modify documents
- [`dotpipe`](../shape/dotpipe.md) - Transform documents