# The `dot` Ecosystem: A Tour

The `dot` ecosystem is a suite of small, focused Python libraries for manipulating nested data structures. Each tool follows the Unix philosophy: it does one thing and does it well. They are designed to be composed together, often in a pipeline, to perform complex data transformations in a clear and predictable way.

This document provides an overview of each tool, its core philosophy, and its primary use case.

## The Two Pillars: Addressing and Logic

The ecosystem is divided into two pillars, each answering a different fundamental question.

### 1. The Addressing Pillar: "What is the data?"

These tools are used to **find and retrieve** data from your nested structures. They are organized in layers of increasing power, following the "Principle of Least Power."

- **`dotget`**: The simplest tool. Gets a value from a single, exact path.
- **`dotstar`**: Adds wildcard matching (`*`) to find all items that match a structural pattern.
- **`dotselect`**: The most powerful user-facing selector. Adds deep searches (`**`) and attribute-based filtering (`[key=value]`).
- **`dotpath`**: The underlying, extensible engine that powers `dotselect` and `dotquery`.

### 2. The Truth Pillar: "Is this statement true?"

These tools are used to **ask questions** about your data. They don't return the data itself, but rather a boolean result (`True`/`False`) or an exit code (`0`/`1`).

- **`dotexists`**: The simplest logical check. Determines if a single, exact path exists.
- **`dotquery`**: A powerful logic engine that evaluates complex, chainable queries against your data.

---

## The Tools: A Detailed Look

### `dotget`: Simple, Exact Addressing

- **Pillar:** Addressing
- **What it does:** Gets a single value from a nested data structure using a precise, dot-separated path.
- **Philosophy:** Do one thing well. `dotget` is intentionally simple, has no dependencies, and its core logic is a single, small function. You are encouraged to **"steal this code"** to avoid adding a dependency for such a simple task.
- **When to use it:** When you know the exact path to the data you need, like reading from a config file or a stable API response.

```python
from dotget import get
data = {"users": [{"name": "Alice"}]}
get(data, "users.0.name")
# => 'Alice'
```

### `dotstar`: Simple Wildcard Addressing

- **Pillar:** Addressing
- **What it does:** Finds all values in a data structure that match a pattern containing wildcards (`*`).
- **Philosophy:** Simple, dependency-free pattern matching. The `*` wildcard matches all items in a list or all values in a dictionary. Like `dotget`, it is simple enough to be "stolen."
- **When to use it:** When you need to extract all data that conforms to a certain structure, like getting all names from a list of user objects.

```python
from dotstar import search
data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
search(data, "users.*.name")
# => ['Alice', 'Bob']
```

### `dotselect`: Advanced Selection

- **Pillar:** Addressing
- **What it does:** The primary user-facing tool for complex queries. It extends the simple wildcard syntax of `dotstar` with descendant selectors (`**`) and predicate filters (`[key=value]`).
- **Philosophy:** Provide a powerful and expressive syntax for the 90% of complex queries, built on the `dotpath` engine.
- **When to use it:** When you need to find data based on its value, without knowing its exact location. It is the go-to tool for most advanced data selection tasks.

```python
from dotselect import find_first
data = {"spec": {"components": [{"type": "server", "ports": [80, 443]}]}}

# Find the ports of the 'server' component, wherever it is.
find_first(data, "**[type=server].ports")
# => [80, 443]
```

### `dotpath`: The Master Addressing Engine

- **Pillar:** Addressing (Engine)
- **What it does:** `dotpath` is the foundational *extensible* addressing library for the ecosystem. It provides the engine for parsing and evaluating the complex paths used by `dotselect` and `dotquery`.
- **Philosophy:** An addressing engine should be an extensible machine. It is the "Lambda of Paths": it allows the path language itself to be extended for specialized use cases.
- **When to use it:** You will typically use `dotpath` indirectly. You would interact with it directly only if you need to create your own custom pathing logic or extend the path language with new capabilities.

### `dotexists`: Simple Existence Check

- **Pillar:** Logic
- **What it does:** Checks for the existence of a value at a precise path.
- **Philosophy:** The logical counterpart to `dotget`. It provides the simplest possible truth check: "Is it there?"
- **When to use it:** To verify that a required key is present in configuration or to guard a `dotget` call in a script.

```python
from dotexists import check
data = {"user": {"name": "Alice", "address": None}}
check(data, "user.name")    # => True
check(data, "user.age")     # => False
```

### `dotquery`: The Logic Engine

- **Pillar:** Logic
- **What it does:** Asks complex, compositional questions about your data and returns a boolean result.
- **Philosophy:** Logic is the anatomy of thought. `dotquery` separates asking a question from retrieving data. It is for validation and conditional logic, not data extraction.
- **When to use it:** When you need to validate a document against a set of rules or make decisions in a script based on the content of your data.

```bash
# In the shell, check if any user is an admin
$ cat users.json | dotquery "any equals role admin"
$ echo $?
# => 0 (True)
```

---

## The Transformation Tools

Building on the addressing and logic pillars, the transformation tools help you modify, process, and reshape your data.

| Tool          | Core Function                                       | Philosophy                               |
|---------------|-----------------------------------------------------|------------------------------------------|
| **`dotmod`**    | Perform immutable modifications to data             | Predictable state change                 |
| **`dotbatch`**  | Apply a sequence of modifications atomically        | Transactions for data                    |
| **`dotpipe`**   | Transform data into a new shape                     | Data transformation as a pipeline        |
| **`dotrelate`** | Perform relational algebra on collections of data   | Bringing database concepts to JSON       |
