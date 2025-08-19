# dotrelate

**Relational operations for collections of documents**

Part of the Collections pillar, `dotrelate` brings fundamental relational algebra operations to JSON-like data structures, enabling SQL-like operations on document collections.

## Overview

`dotrelate` implements core relational operations that work with collections of documents (dictionaries). It provides a functional, composable approach to combining and transforming data from multiple sources.

## Core Operations

### Joins

#### `left_join(left, right, left_on, right_on)`
Performs a left outer join, preserving all items from the left collection.

```python
from collections.dotrelate import left_join

users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"}
]

orders = [
    {"user_id": 1, "product": "Book"},
    {"user_id": 1, "product": "Pen"}
]

result = list(left_join(users, orders, "id", "user_id"))
# [
#   {"id": 1, "name": "Alice", "user_id": 1, "product": "Book"},
#   {"id": 1, "name": "Alice", "user_id": 1, "product": "Pen"},
#   {"id": 2, "name": "Bob"},
#   {"id": 3, "name": "Charlie"}
# ]
```

#### `inner_join(left, right, left_on, right_on)`
Returns only items where matches exist in both collections.

```python
from collections.dotrelate import inner_join

result = list(inner_join(users, orders, "id", "user_id"))
# Only Alice appears (she has orders)
# [
#   {"id": 1, "name": "Alice", "user_id": 1, "product": "Book"},
#   {"id": 1, "name": "Alice", "user_id": 1, "product": "Pen"}
# ]
```

### Projection

#### `project(collection, fields)`
Selects specific fields from each document.

```python
from collections.dotrelate import project

data = [
    {"id": 1, "name": "Alice", "age": 30, "city": "NYC"},
    {"id": 2, "name": "Bob", "age": 25, "city": "LA"}
]

result = list(project(data, ["name", "age"]))
# [
#   {"name": "Alice", "age": 30},
#   {"name": "Bob", "age": 25}
# ]
```

### Set Operations

#### `union(left, right)`
Concatenates two collections (preserves duplicates).

```python
from collections.dotrelate import union

set1 = [{"id": 1}, {"id": 2}]
set2 = [{"id": 3}, {"id": 4}]

result = list(union(set1, set2))
# [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
```

#### `set_difference(left, right)`
Returns items in left that don't exist in right.

```python
from collections.dotrelate import set_difference

all_users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"}
]

active_users = [
    {"id": 1, "name": "Alice"}
]

inactive = list(set_difference(all_users, active_users))
# [{"id": 2, "name": "Bob"}, {"id": 3, "name": "Charlie"}]
```

## Real-World Examples

### User Order Analysis
Combine user data with their orders and extract relevant fields:

```python
users = [
    {"user_id": 1, "name": "Alice", "email": "alice@example.com"},
    {"user_id": 2, "name": "Bob", "email": "bob@example.com"}
]

orders = [
    {"order_id": 101, "user_id": 1, "amount": 50.00},
    {"order_id": 102, "user_id": 1, "amount": 30.00}
]

# Join users with orders
user_orders = list(left_join(users, orders, "user_id", "user_id"))

# Project just the fields we need
summary = list(project(user_orders, ["name", "order_id", "amount"]))
```

### Data Deduplication
Remove duplicates from a dataset:

```python
all_records = [
    {"id": 1, "email": "alice@example.com"},
    {"id": 2, "email": "bob@example.com"},
    {"id": 1, "email": "alice@example.com"},  # Duplicate
]

seen = [{"id": 1, "email": "alice@example.com"}]
unique = list(set_difference(all_records, seen))
```

## Mathematical Foundation

`dotrelate` implements operations from relational algebra:

- **Join (⋈)**: Combines relations based on common attributes
- **Projection (π)**: Selects columns from a relation
- **Union (∪)**: Set union of two relations
- **Difference (-)**: Set difference between relations

These operations form a complete algebra for querying and transforming relational data.

## Integration with Other Tools

`dotrelate` works seamlessly with other dotsuite tools:

```python
from collections.dotrelate import left_join, project
from collections.dotfilter import dotfilter
from truth.dotquery import Query

# Filter users before joining
active_users = dotfilter(users, Query("status equals active"))

# Join with orders
user_orders = left_join(active_users, orders, "id", "user_id")

# Project specific fields
result = project(user_orders, ["name", "product", "amount"])
```

## CLI Usage

```bash
# Join two JSONL files
dotrelate join --left users.jsonl --right orders.jsonl \
    --left-on id --right-on user_id > joined.jsonl

# Project specific fields
dotrelate project --fields name,email < users.jsonl

# Union two files
dotrelate union file1.jsonl file2.jsonl > combined.jsonl
```

## Related Tools

- **[dotfilter](dotfilter.md)**: Filter collections before joining
- **[dotquery](../truth/dotquery.md)**: Create complex join conditions
- **[jsonl-algebra](https://github.com/queelius/jsonl-algebra)**: Production-ready relational operations

## Theory and Motivation

Relational operations are fundamental to data manipulation. By bringing these operations to document-oriented data, `dotrelate` bridges the gap between:

1. **Structured (SQL)** and **semi-structured (JSON)** data paradigms
2. **Set theory** and **practical data processing**
3. **Mathematical rigor** and **developer ergonomics**

The tool demonstrates that relational algebra's elegance extends beyond traditional databases to any collection of structured documents.

For more extensive relational operations and optimizations, see the [jsonl-algebra](https://github.com/queelius/jsonl-algebra) project, which provides a complete implementation of relational algebra for JSONL data.