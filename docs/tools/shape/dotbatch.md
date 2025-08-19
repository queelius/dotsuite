# dotbatch

**Atomic batch operations with rollback support**

Part of the Shape pillar, `dotbatch` provides transactional semantics for multiple modifications, ensuring all changes succeed or none are applied.

## Overview

`dotbatch` brings database-like ACID properties to nested data structure modifications. It executes a batch of operations atomically - if any operation fails, all changes are rolled back.

## Core Concepts

### Atomic Transactions

```python
from shape.dotbatch import Batch

data = {
    "account": {
        "balance": 100,
        "transactions": []
    }
}

# Create a batch of operations
batch = Batch(data)
batch.set("account.balance", 50)
batch.append("account.transactions", {"amount": -50, "type": "withdrawal"})
batch.set("account.last_modified", "2024-01-01")

# Apply all at once (atomic)
result = batch.commit()

# If any operation would fail, nothing is applied
try:
    batch = Batch(data)
    batch.set("account.balance", -100)  # Would fail validation
    batch.delete("required.field")      # Would fail
    result = batch.commit()              # Rolls back, returns original
except BatchError:
    # Original data unchanged
    pass
```

## Operation Types

### Basic Operations

```python
batch = Batch(data)

# Set values
batch.set("user.name", "Alice")
batch.set("user.email", "alice@example.com")

# Update with functions
batch.update("counter", lambda x: x + 1)
batch.update("prices", lambda p: [x * 1.1 for x in p])

# Delete paths
batch.delete("temp.data")
batch.delete("user.old_field")

# Append to lists
batch.append("logs", {"timestamp": now(), "action": "login"})
batch.extend("tags", ["new", "updated"])

# Apply all
result = batch.commit()
```

### Conditional Operations

```python
batch = Batch(data)

# Only apply if condition is met
batch.set_if("user.role", "admin", lambda d: get(d, "user.verified"))
batch.delete_if("cache", lambda d: time() - get(d, "cache.timestamp") > 3600)

# Conditional batch execution
if should_update:
    batch.commit()
else:
    batch.rollback()  # Explicitly discard changes
```

## Validation and Constraints

Add validation to ensure data integrity:

```python
from shape.dotbatch import Batch, ValidationError

def validate_balance(batch, path, value):
    """Ensure balance never goes negative."""
    if value < 0:
        raise ValidationError(f"Balance cannot be negative: {value}")
    return value

batch = Batch(data)
batch.set("account.balance", new_balance, validate=validate_balance)

# Or add global validation
batch.add_validator(lambda d: d.get("account.balance", 0) >= 0)
```

## Real-World Examples

### Bank Transfer (Classic Two-Phase Commit)

```python
def transfer_funds(accounts, from_id, to_id, amount):
    """Transfer funds between accounts atomically."""
    batch = Batch(accounts)
    
    # Debit from source
    from_balance = get(accounts, f"{from_id}.balance")
    if from_balance < amount:
        raise InsufficientFunds()
    
    batch.update(f"{from_id}.balance", lambda b: b - amount)
    batch.append(f"{from_id}.transactions", {
        "type": "debit",
        "amount": -amount,
        "to": to_id,
        "timestamp": now()
    })
    
    # Credit to destination
    batch.update(f"{to_id}.balance", lambda b: b + amount)
    batch.append(f"{to_id}.transactions", {
        "type": "credit",
        "amount": amount,
        "from": from_id,
        "timestamp": now()
    })
    
    # Atomic commit - both succeed or both fail
    return batch.commit()
```

### Shopping Cart Checkout

```python
def checkout_cart(store_data, user_id, cart_items):
    """Process checkout atomically."""
    batch = Batch(store_data)
    
    total = 0
    for item in cart_items:
        product_path = f"products.{item['product_id']}"
        
        # Check inventory
        current_stock = get(store_data, f"{product_path}.stock")
        if current_stock < item['quantity']:
            raise OutOfStock(item['product_id'])
        
        # Update inventory
        batch.update(f"{product_path}.stock", 
                    lambda s: s - item['quantity'])
        
        # Track sales
        batch.update(f"{product_path}.sold", 
                    lambda s: s + item['quantity'])
        
        total += item['quantity'] * get(store_data, f"{product_path}.price")
    
    # Create order
    order = {
        "id": generate_id(),
        "user_id": user_id,
        "items": cart_items,
        "total": total,
        "status": "pending",
        "created_at": now()
    }
    
    batch.append("orders", order)
    batch.set(f"users.{user_id}.cart", [])  # Clear cart
    
    # All succeed or all fail
    return batch.commit(), order['id']
```

### Configuration Update with Rollback

```python
def update_config(config, changes, test_fn):
    """Update configuration with automatic rollback on failure."""
    batch = Batch(config)
    
    # Apply all changes
    for path, value in changes.items():
        batch.set(path, value)
    
    # Test configuration
    new_config = batch.preview()  # See changes without committing
    
    if test_fn(new_config):
        return batch.commit()  # Tests passed, apply
    else:
        batch.rollback()       # Tests failed, discard
        raise ConfigTestFailed()
```

## Transaction Log

Track all operations for audit:

```python
batch = Batch(data, track_operations=True)

batch.set("user.name", "Alice")
batch.update("user.login_count", lambda x: x + 1)

# Get operation log
log = batch.get_operations()
# [
#   {"op": "set", "path": "user.name", "value": "Alice"},
#   {"op": "update", "path": "user.login_count", "fn": "<lambda>"}
# ]

# Replay operations on different data
other_data = {}
for op in log:
    apply_operation(other_data, op)
```

## Nested Batches

Create savepoints with nested batches:

```python
outer = Batch(data)
outer.set("status", "processing")

# Nested batch for risky operations
inner = outer.nested()
try:
    inner.set("risky.operation", compute_value())
    inner.set("another.risky", external_api_call())
    inner.commit()  # Commit to outer batch
except Exception:
    inner.rollback()  # Only rolls back inner changes
    outer.set("status", "partial_failure")

outer.commit()  # Apply outer changes
```

## Mathematical Foundation

`dotbatch` implements a transaction monad with:
- **Atomicity**: All operations succeed or all fail
- **Consistency**: Validation ensures invariants
- **Isolation**: Changes invisible until commit
- **Durability**: Immutable structures preserve history

The batch forms a monoid under composition:
- **Identity**: Empty batch
- **Associativity**: Batch composition is associative
- **Closure**: Composing batches yields a batch

## Performance Considerations

- **Lazy evaluation**: Operations are queued, not executed until commit
- **Single pass application**: All changes applied in one traversal
- **Structural sharing**: Unchanged parts share memory
- **Rollback cost**: O(1) - just return original data

## Related Tools

- **[dotmod](dotmod.md)** - Individual modifications
- **[dotpipe](dotpipe.md)** - Sequential transformations
- **[dotget](../depth/dotget.md)** - Read values for validation