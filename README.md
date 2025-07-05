# The Dot Ecosystem

> "What started as a single, humble function evolved into a complete, coherent ecosystem for manipulating data structures—a journey in API design guided by the principles of purity, pedagogy, and the principle of least power."

The **dot ecosystem** is a suite of composable tools for working with nested data structures like JSON, YAML, and Python dictionaries. Each tool follows the Unix philosophy: it does one thing exceptionally well, and they're designed to work together seamlessly.

## Installation

```bash
# Install the entire ecosystem
pip install dotsuite

# Or install only what you need
pip install dotsuite[addressing]    # dotget, dotstar, dotselect, dotpath
pip install dotsuite[logic]         # dotexists, dotany, dotall, dotquery
pip install dotsuite[transform]     # dotmod, dotbatch, dotpipe, dotpluck
pip install dotsuite[collections]   # dotfilter, dotrelate

# Individual tools
pip install dotsuite[dotget,dotquery,dotmod]
```

## Motivation

It always starts with a simple problem. You have a nested dictionary or JSON payload, and you need to get a value buried deep inside. You write `data['user']['contacts'][0]['email']` and pray that no key or index is missing along the way, lest your program crash with a `KeyError`. This leads to brittle, defensive code full of try/except blocks.

What began as a simple helper function—`dotget`—evolved through questions and insights into a complete ecosystem. The result is a mathematically grounded, pedagogically structured collection of tools that makes data manipulation predictable, safe, and expressive.

## The Three Pillars

The ecosystem is built on three fundamental pillars, each answering a core question about data:

### 🎯 **Depth Pillar** - "Where is the data?"
Tools for finding and extracting values from within documents.

### ✅ **Truth Pillar** - "Is this assertion true?" 
Tools for asking boolean questions and validating data.

### 🔄 **Shape Pillar** - "How should the data be transformed?"
Tools for reshaping and modifying data structures.

These pillars operate on single documents, and then **lift** to collections through boolean algebra and relational operations.

## Quick Start

```python
from dotget import get
from dotstar import search  
from dotquery import Query
from dotmod import set_

# Simple exact addressing
data = {"users": [{"name": "Alice", "role": "admin"}]}
name = get(data, "users.0.name")  # "Alice"

# Pattern matching with wildcards
all_names = search(data, "users.*.name")  # ["Alice"]

# Boolean logic queries
is_admin = Query("equals role admin").check(data["users"][0])  # True

# Immutable modifications
new_data = set_(data, "users.0.status", "active")
```

## The Tools

### Depth Pillar: Addressing & Extraction

| Tool | Purpose | Example |
|------|---------|---------|
| **[`dotget`](dotget/)** | Simple exact paths | `get(data, "user.name")` |
| **[`dotstar`](dotstar/)** | Wildcard patterns | `search(data, "users.*.name")` |
| **[`dotselect`](dotselect/)** | Advanced selection with predicates | `find_first(data, "users[role=admin].name")` |
| **[`dotpath`](dotpath/)** | Extensible path engine | Powers other tools, JSONPath-compatible |
| **[`dotpluck`](dotpluck/)** | Extract multiple values | Creates new structures from selections |

**Philosophy:** Start simple with `dotget` for known paths, add `dotstar` for patterns, use `dotselect` for complex queries. The `dotpath` engine underpins them all with extensible, Turing-complete addressing.

### Truth Pillar: Logic & Validation  

| Tool | Purpose | Example |
|------|---------|---------|
| **[`dotexists`](dotexists/)** | Path existence | `check(data, "user.email")` |
| **[`dotany`](dotany/)** | Existential quantifier | `check(data, "users.*.role", equals="admin")` |
| **[`dotall`](dotall/)** | Universal quantifier | `check(data, "users.*.status", equals="active")` |
| **[`dotquery`](dotquery/)** | Compositional logic engine | `Query("any equals role admin").check(data)` |
| **[`dotfilter`](dotfilter/)** | Boolean algebra on collections | Lazy querysets with full boolean logic |

**Philosophy:** Boolean questions should be separate from data extraction. Start with `dotexists` for simple checks, compose complex logic with `dotquery`, and use `dotfilter` for collection-level boolean algebra.

### Shape Pillar: Transformation & Mutation

| Tool | Purpose | Example |
|------|---------|---------|
| **[`dotmod`](dotmod/)** | Surgical modifications | `set_(data, "user.status", "inactive")` |
| **[`dotbatch`](dotbatch/)** | Atomic transactions | Apply multiple changes safely |
| **[`dotpipe`](dotpipe/)** | Data transformation pipelines | Reshape documents into new forms |

**Philosophy:** Immutable by default. `dotmod` for precise edits, `dotbatch` for transactional safety, `dotpipe` for creating new data shapes.

### Collections: Boolean & Relational Algebra

| Tool | Purpose | Domain |
|------|---------|--------|
| **[`dotfilter`](dotfilter/)** | Boolean algebra on document collections | Filter, intersect, union with lazy evaluation |
| **[`dotrelate`](dotrelate/)** | Relational operations | Join, project, union collections like database tables |

**Philosophy:** Lift single-document operations to collections. `dotfilter` provides set operations with boolean logic, while `dotrelate` enables database-style joins and projections.

## Design Principles

- **🧩 Compositionality:** Every tool composes cleanly with others
- **🔒 Immutability:** Original data is never modified  
- **📚 Pedagogical:** Simple tools graduate to powerful ones
- **🎯 Single Purpose:** Each tool has one clear responsibility
- **🔗 Interoperability:** Common patterns work across all tools
- **⚡ Performance:** Lazy evaluation and efficient algorithms
- **🛡️ Safety:** Graceful handling of missing paths and malformed data

## Common Patterns

### The "Steal This Code" Philosophy

Many tools are intentionally simple enough that you can copy their core logic rather than add a dependency:

```python
# The essence of dotget
def get(data, path, default=None):
    try:
        for segment in path.split('.'):
            data = data[int(segment)] if segment.isdigit() and isinstance(data, list) else data[segment]
        return data
    except (KeyError, IndexError, TypeError):
        return default
```

### Command-Line First

Every tool works from the command line, making them perfect for shell scripts and data pipelines:

```bash
# Check if any user is an admin
cat users.json | dotquery "any equals role admin" && echo "Admin found"

# Extract all email addresses  
cat contacts.json | dotstar "contacts.*.email" > emails.txt

# Join users with their orders
dotrelate join --on="user_id" users.jsonl orders.jsonl
```

### Dual APIs: Programmatic and Declarative

Many tools offer both Python APIs and serializable JSON formats:

```python
# Programmatic
query = Query(equals('role', 'admin') & greater('login_count', 10))

# Declarative  
query = Query("equals role admin and greater login_count 10")

# Both produce the same AST
assert query.ast == other_query.ast
```

## From Simple to Sophisticated

The ecosystem is designed as a learning journey:

1. **Hello World:** `dotget`, `dotexists` - O(1) mental load
2. **Patterns:** Add `dotstar`, `dotmod` - wildcards and basic changes  
3. **Power User:** `dotselect`, `dotquery`, `dotpipe` - complex operations
4. **Expert:** `dotpath`, `dotfilter`, `dotrelate` - extensible engines

Each stage builds on the previous, with no tool becoming obsolete. A `dotget` call is still the right choice when you know the exact path.

## Mathematical Foundation

The ecosystem is built on solid mathematical principles:

- **Addressing** forms a free algebra on selectors (Turing-complete via user-defined reducers)
- **Logic** implements Boolean algebra with homomorphic lifting to set operations  
- **Transformations** are endofunctors on document spaces with monoid composition
- **Collections** lift via functorial map/filter operations preserving algebraic structure

This ensures predictable composition, parallelizability, and mathematical correctness.

## Individual Tool Documentation

Each tool has comprehensive documentation in its subdirectory:

- [**dotget**](dotget/) - Simple exact addressing
- [**dotstar**](dotstar/) - Wildcard pattern matching  
- [**dotselect**](dotselect/) - Advanced selection with predicates
- [**dotpath**](dotpath/) - Extensible path engine
- [**dotexists**](dotexists/) - Path existence checking
- [**dotany**](dotany/) - Existential quantifier  
- [**dotall**](dotall/) - Universal quantifier
- [**dotquery**](dotquery/) - Compositional logic engine
- [**dotmod**](dotmod/) - Immutable modifications
- [**dotbatch**](dotbatch/) - Atomic transactions
- [**dotpipe**](dotpipe/) - Data transformation pipelines  
- [**dotpluck**](dotpluck/) - Value extraction and reshaping
- [**dotfilter**](dotfilter/) - Boolean algebra on collections
- [**dotrelate**](dotrelate/) - Relational operations

## Contributing

The dot ecosystem welcomes contributions! Each tool lives in its own directory with its own tests and documentation. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. Use freely, modify as needed, and contribute back when you can.

---

*The dot ecosystem: from simple paths to sophisticated data algebras, one tool at a time.*
