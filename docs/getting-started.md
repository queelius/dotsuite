# Getting Started

## Installation

```bash
# Install from PyPI (once published)
pip install dotsuite

# Or install from source
git clone https://github.com/yourusername/dotsuite.git
cd dotsuite
pip install -e .
```

## Quick Example

```python
# After pip install dotsuite:
from dotsuite.depth.dotget import get
from dotsuite.depth.dotstar import search
from dotsuite.shape.dotmod import set_

# Or if using source install:
# from depth.dotget.core import get
# from depth.dotstar.core import search
# from shape.dotmod.core import set_

# Your nested data
data = {
    "users": [
        {"name": "Alice", "age": 30, "role": "admin"},
        {"name": "Bob", "age": 25, "role": "user"}
    ]
}

# Get a specific value
name = get(data, "users.0.name")  # "Alice"

# Search with wildcards
all_names = search(data, "users.*.name")  # ["Alice", "Bob"]

# Modify data (returns new copy)
new_data = set_(data, "users.0.role", "superadmin")
```

## The Three Pillars

**Depth** - Finding data:

- `dotget` - Simple path access
- `dotstar` - Wildcard patterns

**Truth** - Validating data:

- `dotexists` - Check if path exists
- `dotany`/`dotall` - Quantifiers

**Shape** - Transforming data:

- `dotmod` - Immutable modifications
- `dotbatch` - Atomic transactions

## Learn More

Ready to dive deeper? Check out:

- [Philosophy](philosophy.md) - The design principles behind dotsuite
- [Ecosystem](ecosystem.md) - Complete tool overview
- [Examples](https://github.com/yourusername/dotsuite/tree/main/examples) - Real-world usage

## For Developers

```bash
# Development setup with testing tools
make install-dev
make test
make docs-serve  # View docs at http://127.0.0.1:8000
```
