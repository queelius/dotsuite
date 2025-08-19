# dotall

**Universal quantifier for collections**

Part of the Truth pillar, `dotall` checks if all items in a collection satisfy a condition.

## Overview

`dotall` implements the universal quantifier (∀) from mathematical logic, returning `True` if every item in a collection matches a specified value at a given path.

## Basic Usage

```python
from truth.dotall import all_match

users = [
    {"name": "Alice", "verified": True},
    {"name": "Bob", "verified": True},
    {"name": "Charlie", "verified": True}
]

# Check if all users are verified
all_verified = all_match(users, "verified", True)  # True

# Add an unverified user
users.append({"name": "David", "verified": False})
all_verified = all_match(users, "verified", True)  # False
```

## Nested Paths

Works with nested data structures:

```python
data = [
    {"user": {"status": {"active": True}}},
    {"user": {"status": {"active": True}}},
    {"user": {"status": {"active": True}}}
]

# Check if all users are active
all_active = all_match(data, "user.status.active", True)  # True
```

## Edge Cases

### Empty Collections (Vacuous Truth)
Returns `True` for empty collections (vacuous truth in logic):

```python
empty = []
result = all_match(empty, "any.path", "value")  # True
# "All items in an empty set satisfy any condition"
```

### Missing Paths
Items with missing paths are treated as non-matching:

```python
data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob"}  # Missing age
]

# Bob doesn't have age field
all_age_30 = all_match(data, "age", 30)  # False
```

## Mathematical Properties

- **Vacuous truth**: Empty collections always return `True`
- **Universal quantification**: ∀x ∈ collection : predicate(x)
- **Dual of dotany**: `all` and `any` form a duality in boolean logic
- **De Morgan's laws**: `not(all(p))` ≡ `any(not(p))`

## Integration with dotquery

`dotall` is used internally by `dotquery` for collection queries:

```python
from truth.dotquery import Query

# These are equivalent:
q = Query("all users.verified equals true")
# vs
from truth.dotall import all_match
result = all_match(users, "verified", True)
```

## Real-World Examples

### Data Validation
```python
# Ensure all products have required fields
products = [
    {"name": "Widget", "price": 9.99, "sku": "W001"},
    {"name": "Gadget", "price": 19.99, "sku": "G001"}
]

# All products must have positive prices
valid = all_match(products, "price", lambda x: x > 0)
```

### Permission Checking
```python
# Check if all team members have access
team = [
    {"name": "Alice", "permissions": ["read", "write"]},
    {"name": "Bob", "permissions": ["read", "write"]}
]

# All must have write permission
can_edit = all_match(team, "permissions", lambda p: "write" in p)
```

## Related Tools

- **[dotany](dotany.md)** - Existential quantifier (at least one matches)
- **[dotexists](dotexists.md)** - Check path existence
- **[dotquery](dotquery.md)** - Complex boolean queries
- **[dotfilter](../collections/dotfilter.md)** - Filter collections