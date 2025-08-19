# dotpipe

**Composable transformation pipelines**

Part of the Shape pillar, `dotpipe` enables building complex data transformations through function composition.

## Overview

`dotpipe` provides a clean, functional approach to chaining data transformations, making complex operations readable and maintainable.

## Basic Usage

```python
from shape.dotpipe import pipe, compose

# Create a pipeline
pipeline = pipe(
    lambda x: x * 2,      # Double
    lambda x: x + 10,     # Add 10
    lambda x: x / 2       # Halve
)

result = pipeline(5)  # ((5 * 2) + 10) / 2 = 10
```

## Working with Nested Data

Combine with other dotsuite tools:

```python
from shape.dotpipe import pipe
from shape.dotmod import set_, update
from depth.dotget import get

# Complex transformation pipeline
process_user = pipe(
    lambda d: set_(d, "user.verified", True),
    lambda d: update(d, "user.name", str.upper),
    lambda d: set_(d, "user.processed_at", "2024-01-01"),
    lambda d: delete(d, "user.temp_data")
)

data = {
    "user": {
        "name": "alice",
        "verified": False,
        "temp_data": "cleanup"
    }
}

result = process_user(data)
# {
#     "user": {
#         "name": "ALICE",
#         "verified": True,
#         "processed_at": "2024-01-01"
#     }
# }
```

## Compose vs Pipe

- **`pipe`**: Left-to-right composition (first → last)
- **`compose`**: Right-to-left composition (last → first)

```python
from shape.dotpipe import pipe, compose

# These are equivalent:
pipeline1 = pipe(f, g, h)       # h(g(f(x)))
pipeline2 = compose(h, g, f)    # h(g(f(x)))
```

## Partial Pipelines

Build reusable transformation components:

```python
# Reusable transformations
normalize_user = pipe(
    lambda d: update(d, "email", str.lower),
    lambda d: update(d, "name", str.title)
)

add_timestamps = pipe(
    lambda d: set_(d, "created_at", now()),
    lambda d: set_(d, "updated_at", now())
)

validate_user = pipe(
    lambda d: d if get(d, "email") else raise_error("Email required"),
    lambda d: d if get(d, "name") else raise_error("Name required")
)

# Combine into full pipeline
process_new_user = pipe(
    normalize_user,
    validate_user,
    add_timestamps
)
```

## Real-World Examples

### Data Cleaning Pipeline
```python
clean_product_data = pipe(
    # Normalize strings
    lambda d: update(d, "name", lambda n: n.strip().title()),
    lambda d: update(d, "sku", lambda s: s.upper().replace("-", "")),
    
    # Validate price
    lambda d: set_(d, "price", max(0, get(d, "price") or 0)),
    
    # Add computed fields
    lambda d: set_(d, "display_price", f"${get(d, 'price'):.2f}"),
    
    # Remove internal fields
    lambda d: delete(d, "_internal_id"),
    lambda d: delete(d, "_raw_import")
)
```

### API Response Transformation
```python
transform_api_response = pipe(
    # Extract data envelope
    lambda r: get(r, "data") or {},
    
    # Rename fields
    lambda d: set_(d, "userId", get(d, "user_id")),
    lambda d: delete(d, "user_id"),
    
    # Flatten nested structure
    lambda d: {**d, **get(d, "attributes", {})},
    lambda d: delete(d, "attributes"),
    
    # Add metadata
    lambda d: set_(d, "fetched_at", datetime.now().isoformat())
)
```

### Form Processing
```python
process_form_submission = pipe(
    # Sanitize inputs
    lambda f: {k: v.strip() if isinstance(v, str) else v 
               for k, v in f.items()},
    
    # Validate required fields
    lambda f: f if all(get(f, field) for field in ["email", "name"]) 
              else raise_error("Missing required fields"),
    
    # Normalize email
    lambda f: update(f, "email", str.lower),
    
    # Hash password if present
    lambda f: update(f, "password", hash_password) if get(f, "password") else f,
    
    # Add metadata
    lambda f: set_(f, "submitted_at", datetime.now()),
    lambda f: set_(f, "ip_address", get_client_ip())
)
```

## Async Pipelines

For async transformations:

```python
from shape.dotpipe import async_pipe

process_async = async_pipe(
    fetch_user_data,      # async function
    enrich_with_api,      # async function  
    save_to_database      # async function
)

result = await process_async(user_id)
```

## Mathematical Foundation

`dotpipe` implements function composition from category theory:
- **Associativity**: `pipe(f, pipe(g, h))` = `pipe(pipe(f, g), h)`
- **Identity**: `pipe(identity, f)` = `f` = `pipe(f, identity)`
- **Functorial**: Preserves structure of transformations

## Related Tools

- **[dotmod](dotmod.md)** - Individual modifications
- **[dotbatch](dotbatch.md)** - Atomic batch operations
- **[dotpluck](dotpluck.md)** - Extract and reshape data