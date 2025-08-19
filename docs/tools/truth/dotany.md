# dotany

**Existential quantifier for collections**

Part of the Truth pillar, `dotany` checks if at least one item in a collection satisfies a condition.

## Overview

`dotany` implements the existential quantifier (∃) from mathematical logic, returning `True` if any item in a collection matches a specified value at a given path.

## Basic Usage

```python
from truth.dotany import any_match

users = [
    {"name": "Alice", "role": "admin"},
    {"name": "Bob", "role": "user"},
    {"name": "Charlie", "role": "user"}
]

# Check if any user is an admin
has_admin = any_match(users, "role", "admin")  # True

# Check if any user is named "David"
has_david = any_match(users, "name", "David")  # False
```

## Nested Paths

Works with nested data structures:

```python
data = [
    {"user": {"profile": {"age": 25}}},
    {"user": {"profile": {"age": 30}}},
    {"user": {"profile": {"age": 35}}}
]

# Check if any user is exactly 30
has_thirty = any_match(data, "user.profile.age", 30)  # True
```

## Edge Cases

### Empty Collections
Returns `False` for empty collections (no items to match):

```python
empty = []
result = any_match(empty, "any.path", "value")  # False
```

### Missing Paths
Items with missing paths are treated as non-matching:

```python
data = [
    {"name": "Alice"},
    {"name": "Bob", "age": 30}
]

# Only Bob has age field
has_age_30 = any_match(data, "age", 30)  # True
has_age_25 = any_match(data, "age", 25)  # False
```

## Mathematical Properties

- **Short-circuit evaluation**: Stops as soon as a match is found
- **Existential quantification**: ∃x ∈ collection : predicate(x)
- **Dual of dotall**: `any` and `all` form a duality in boolean logic

## Integration with dotquery

`dotany` is used internally by `dotquery` for collection queries:

```python
from truth.dotquery import Query

# These are equivalent:
q = Query("any users.role equals admin")
# vs
from truth.dotany import any_match
result = any_match(users, "role", "admin")
```

## Related Tools

- **[dotall](dotall.md)** - Universal quantifier (all items must match)
- **[dotexists](dotexists.md)** - Check path existence
- **[dotquery](dotquery.md)** - Complex boolean queries
- **[dotfilter](../collections/dotfilter.md)** - Filter collections