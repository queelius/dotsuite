# dotquery

**Compositional logic engine for complex boolean queries**

Part of the Truth pillar, `dotquery` provides a powerful, composable system for building and evaluating complex boolean queries on nested data structures.

## Overview

`dotquery` offers two complementary APIs:
1. **Programmatic API** - Build queries using Python objects
2. **DSL (Domain Specific Language)** - Write queries as human-readable strings

## DSL Syntax

The DSL provides an intuitive way to express complex queries:

```python
from truth.dotquery import Query

# Simple equality check
q = Query("status equals active")

# Comparison operators
q = Query("age greater 18")
q = Query("price less 100")

# Boolean logic
q = Query("(role equals admin) and (active equals true)")
q = Query("(status equals pending) or (status equals processing)")
q = Query("not deleted equals true")

# Nested paths
q = Query("user.profile.age greater 21")

# Quantifiers for collections
q = Query("any items.price greater 100")
q = Query("all users.verified equals true")
```

## Supported Operators

### Comparison Operators
- `equals`, `eq`, `=`, `==` - Equality
- `not_equals`, `ne`, `!=` - Inequality  
- `greater`, `gt`, `>` - Greater than
- `greater_equal`, `ge`, `>=` - Greater or equal
- `less`, `lt`, `<` - Less than
- `less_equal`, `le`, `<=` - Less or equal
- `contains`, `in` - Contains (for lists/strings)
- `matches`, `regex` - Regular expression matching
- `exists` - Path exists and has truthy value

### Logical Operators
- `and` - Both conditions must be true
- `or` - At least one condition must be true
- `not` - Negates the condition

### Quantifiers
- `any` - At least one item matches (default for collections)
- `all` - All items must match (vacuous truth for empty collections)

## Programmatic API

Build queries programmatically using the Q builder:

```python
from truth.dotquery import Q

# Simple queries
q = Q("status").equals("active")
q = Q("age").greater(18)

# Combine with logical operators
q = Q("role").equals("admin") & Q("active").equals(True)
q = Q("status").equals("pending") | Q("status").equals("processing")
q = ~Q("deleted").equals(True)

# Quantifiers
q = Q("scores").all().greater(60)  # All scores > 60
q = Q("tags").contains("python")   # Any tag equals "python" (default)
```

## Real-World Examples

### User Authorization
```python
# Can user perform action?
can_edit = Query("""
    (role equals admin) or 
    ((role equals editor) and (verified equals true))
""")

user = {"role": "editor", "verified": True}
if can_edit.check(user):
    # Allow edit
    pass
```

### Data Validation
```python
# Validate configuration
valid_config = Query("""
    (database.host exists) and
    (database.port greater 0) and
    (database.port less 65536)
""")

config = {"database": {"host": "localhost", "port": 5432}}
assert valid_config.check(config)
```

### Filtering Collections
```python
from collections.dotfilter import dotfilter

users = [
    {"name": "Alice", "age": 30, "role": "admin"},
    {"name": "Bob", "age": 25, "role": "user"},
    {"name": "Charlie", "age": 35, "role": "user"}
]

# Find admin users over 25
admins = dotfilter(users, Query("(role equals admin) and (age greater 25)"))
```

## Error Handling

The DSL parser provides specific exception types for better error handling:

```python
from truth.dotquery.core import DSLError, DSLSyntaxError, UnknownOperatorError

try:
    q = Query("status unknownop value")
except UnknownOperatorError as e:
    print(f"Unknown operator: {e}")
except DSLSyntaxError as e:
    print(f"Syntax error: {e}")
except DSLError as e:
    print(f"General DSL error: {e}")
```

## Mathematical Foundation

`dotquery` implements a complete boolean algebra with:
- **Expressions**: Abstract syntax trees (AST) for query composition
- **Operators**: Closed under boolean operations
- **Quantifiers**: Universal (∀) and existential (∃) quantification
- **Homomorphism**: Queries lift to set operations on collections

## Related Tools

- **[dotexists](dotexists.md)** - Simple path existence checking
- **[dotequals](dotequals.md)** - Direct equality comparisons
- **[dotany](dotany.md)** / **[dotall](dotall.md)** - Collection quantifiers
- **[dotfilter](../collections/dotfilter.md)** - Filter collections using queries