# dotfilter

> Boolean algebra on document collections - lifting single-document logic to sets

## Overview

`dotfilter` represents the Collections dimension's core capability: lifting Truth pillar operations to work on collections. It filters documents based on boolean queries while providing lazy evaluation through QuerySet operations.

This tool bridges single-document validation (Truth pillar) with collection-level operations, enabling set operations like union, intersection, and difference on filtered results.

## Installation

```bash
# As part of dotsuite
pip install dotsuite

# Or from source
cd src/collections/dotfilter
pip install -e .
```

## Core Functions

### `filter_docs(docs, query_str)`

Filter a collection of documents using a boolean query.

```python
from collections.dotfilter.core import filter_docs

docs = [
    {"user": "alice", "role": "admin", "active": True},
    {"user": "bob", "role": "user", "active": True},
    {"user": "charlie", "role": "admin", "active": False}
]

# Filter using query strings
admins = filter_docs(docs, "equals role admin")
# Returns: [{"user": "alice", ...}, {"user": "charlie", ...}]

active_admins = filter_docs(docs, "equals role admin and equals active true")
# Returns: [{"user": "alice", ...}]
```

### `filter_by_path(docs, path, value)`

Simple filtering by path equality.

```python
from collections.dotfilter.core import filter_by_path

# Direct path filtering
active_users = filter_by_path(docs, "active", True)
# Returns: [{"user": "alice", ...}, {"user": "bob", ...}]

admin_users = filter_by_path(docs, "role", "admin")
# Returns: [{"user": "alice", ...}, {"user": "charlie", ...}]
```

### `QuerySet` Class

Lazy evaluation with set operations.

```python
from collections.dotfilter.core import QuerySet

# Create QuerySets (lazy - no evaluation yet)
all_docs = QuerySet(docs)
admins = all_docs.filter("equals role admin")
active = all_docs.filter("equals active true")

# Set operations (still lazy)
active_admins = admins.intersection(active)
admin_or_active = admins.union(active)
inactive_admins = admins.difference(active)

# Evaluate when needed
result = list(active_admins)  # Now it evaluates
```

## Command Line Usage

```bash
# Filter JSON documents
cat users.json | dotfilter "equals role admin"

# Complex queries
cat users.json | dotfilter "equals active true and not equals role guest"

# Simple path filtering
cat users.json | dotfilter --path role --value admin

# Count results
cat users.json | dotfilter "equals active true" --count
```

## Common Use Cases

### 1. User Management

Filter users based on roles and status:

```python
users = [
    {"id": 1, "name": "Alice", "role": "admin", "active": True, "login_count": 42},
    {"id": 2, "name": "Bob", "role": "user", "active": True, "login_count": 5},
    {"id": 3, "name": "Charlie", "role": "admin", "active": False, "login_count": 0},
    {"id": 4, "name": "Diana", "role": "moderator", "active": True, "login_count": 15}
]

# Find active admins
active_admins = filter_docs(users, "equals role admin and equals active true")

# Find users who need activation
inactive = filter_docs(users, "equals active false")

# Find power users
power_users = filter_docs(users, "greater_than login_count 10")
```

### 2. Configuration Validation

Check configurations across multiple environments:

```python
configs = [
    {"env": "prod", "debug": False, "ssl": True, "port": 443},
    {"env": "staging", "debug": True, "ssl": True, "port": 443},
    {"env": "dev", "debug": True, "ssl": False, "port": 8080}
]

# Find misconfigured environments
issues = filter_docs(configs, "equals debug true and equals env prod")
if issues:
    print("WARNING: Debug enabled in production!")

# Find secure environments
secure = filter_docs(configs, "equals ssl true")
```

### 3. Log Analysis

Filter log entries:

```python
logs = [
    {"timestamp": "2024-01-01T10:00:00", "level": "ERROR", "service": "api", "message": "Connection failed"},
    {"timestamp": "2024-01-01T10:01:00", "level": "INFO", "service": "api", "message": "Request processed"},
    {"timestamp": "2024-01-01T10:02:00", "level": "ERROR", "service": "db", "message": "Query timeout"},
    {"timestamp": "2024-01-01T10:03:00", "level": "WARN", "service": "api", "message": "Slow response"}
]

# Find all errors
errors = filter_docs(logs, "equals level ERROR")

# Find API errors specifically
api_errors = filter_docs(logs, "equals level ERROR and equals service api")

# Find non-info logs
important = filter_docs(logs, "not equals level INFO")
```

### 4. Lazy Set Operations

Combine filters efficiently:

```python
products = QuerySet([
    {"name": "Laptop", "price": 999, "category": "electronics", "in_stock": True},
    {"name": "Mouse", "price": 25, "category": "electronics", "in_stock": True},
    {"name": "Desk", "price": 299, "category": "furniture", "in_stock": False},
    {"name": "Chair", "price": 199, "category": "furniture", "in_stock": True}
])

# Define filters (lazy)
electronics = products.filter("equals category electronics")
in_stock = products.filter("equals in_stock true")
affordable = products.filter("less_than price 200")

# Combine filters (still lazy)
available_electronics = electronics.intersection(in_stock)
budget_items = affordable.intersection(in_stock)

# Only evaluates when needed
for item in available_electronics:
    print(f"{item['name']}: ${item['price']}")
```

## Query Language

`dotfilter` uses the query language from `dotquery`:

### Comparison Operators
- `equals PATH VALUE` - Check equality
- `not_equals PATH VALUE` - Check inequality
- `greater_than PATH VALUE` - Numeric comparison
- `less_than PATH VALUE` - Numeric comparison
- `contains PATH VALUE` - String/list containment
- `matches PATH PATTERN` - Regex matching

### Logical Operators
- `and` - Both conditions must be true
- `or` - Either condition must be true
- `not` - Negate a condition

### Examples
```bash
# Simple equality
"equals status active"

# Multiple conditions
"equals role admin and equals active true"

# Complex logic
"(equals category electronics or equals category computers) and less_than price 1000"

# Negation
"not equals status deleted"
```

## Philosophy

`dotfilter` embodies the Collections dimension philosophy:
1. **Homomorphic Lifting**: Truth operations on documents lift to set operations on collections
2. **Lazy Evaluation**: QuerySets defer computation until needed
3. **Composability**: Set operations combine naturally
4. **Simplicity**: Complex filtering through simple boolean algebra

## Comparison with Other Tools

| Tool | Scope | Purpose | Returns |
|------|-------|---------|---------|
| `dotquery` | Single document | Boolean evaluation | True/False |
| `dotfilter` | Collection | Filter by boolean query | Filtered documents |
| `dotany` | Collection | Existential check | True/False |
| `dotall` | Collection | Universal check | True/False |

## Performance Notes

- **Lazy Evaluation**: QuerySets don't evaluate until iteration
- **Short-Circuit**: Boolean operators short-circuit when possible
- **Memory Efficient**: Streaming evaluation for large collections
- **Set Operations**: Optimized for common patterns

## Production Implementation

For a production-ready implementation with advanced features, see [JAF (Just Another Flow)](https://github.com/realazthat/jaf), which extends these concepts with:
- Streaming evaluation for large datasets
- S-expression query language
- Advanced path operations (regex, fuzzy matching)
- Pipeline composition similar to dotpipe
- Index-preserving result sets

## See Also

- [`dotquery`](../truth/dotquery.md) - Single-document boolean queries
- [`dotany`](../truth/dotany.md) - Check if any document matches
- [`dotall`](../truth/dotall.md) - Check if all documents match
- [`dotrelate`](../collections/dotrelate.md) - Relational operations on collections