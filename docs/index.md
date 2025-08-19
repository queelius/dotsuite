# Welcome to the Dot Notation Universe

The `dotsuite` ecosystem provides a comprehensive, pedagogically-designed suite of tools for manipulating nested data structures using dot notation.

## Project Status: v0.9-beta

✅ **Feature Complete**: All 15 core tools implemented across 4 pillars  
✅ **Comprehensive Testing**: 367 tests passing with 100% coverage  
✅ **Type Hints**: Full type annotations for IDE support  
✅ **CLI Support**: All tools accessible from command line  
✅ **DSL Parser**: Human-friendly query syntax for dotquery  

## Quick Overview

The ecosystem is organized around three fundamental pillars plus collections:

- **🎯 Depth Pillar**: Finding and extracting data (`dotget`, `dotstar`, `dotselect`, `dotpath`)
- **✅ Truth Pillar**: Boolean logic and validation (`dotexists`, `dotequals`, `dotany`, `dotall`, `dotquery`)
- **🔄 Shape Pillar**: Data transformation (`dotmod`, `dotbatch`, `dotpipe`, `dotpluck`)
- **📚 Collections**: Relational operations (`dotfilter`, `dotrelate`)

## Get Started

- [Getting Started](getting-started.md) - Installation and first steps
- [Philosophy](philosophy.md) - Design principles and motivation
- [Ecosystem Overview](ecosystem.md) - Complete tool reference

## Why dotsuite?

1. **Pedagogical Design**: Learn data manipulation concepts through clear, focused tools
2. **Composability**: Unix philosophy - each tool does one thing well
3. **Mathematical Foundation**: Built on solid theoretical principles
4. **Safe by Default**: Immutable operations, graceful handling of missing data
5. **Progressive Enhancement**: Start simple, add complexity as needed

## Example

```python
from depth.dotget import get
from truth.dotquery import Query
from collections.dotfilter import dotfilter

data = [
    {"user": {"name": "Alice", "age": 30, "role": "admin"}},
    {"user": {"name": "Bob", "age": 25, "role": "user"}}
]

# Filter admins over 25
admins = dotfilter(data, Query("(user.role equals admin) and (user.age greater 25)"))

# Extract names
names = [get(doc, "user.name") for doc in admins]  # ["Alice"]
```

## Related Projects

- [jsonl-algebra](https://github.com/queelius/jsonl-algebra) - Production-ready relational operations for JSONL
- [JAF](https://github.com/queelius/jaf) - JSON Array Filter with advanced capabilities

## Contributing

We welcome contributions! See our [GitHub repository](https://github.com/queelius/dotsuite) for:
- Source code
- Issue tracking
- Development guidelines
- Test suite (367 tests!)

---

*"What started as a single, humble function evolved into a complete, coherent ecosystem for manipulating data structures."*