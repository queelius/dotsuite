# Proposal: The Three Pillars of the `dot` Ecosystem

This document proposes a formal, three-pillar structure for the `dot` ecosystem. This model clarifies the purpose of each tool, establishes a clear pedagogical progression for users, and provides a robust framework for future development.


## The Core Idea: Depth, Truth, and Breadth

The `dot` ecosystem is organized into three distinct pillars, each answering a fundamental question about data:

1.  **The Addressing Pillar (Depth):** Answers **"Where is the data?"** within a *single document*.
2.  **The Logic Pillar (Truth):** Answers **"Is this true?"** about a *single document*.
3.  **The Collections Pillar (Breadth):** Operates on a *collection of documents* to answer **"Which documents?"** or **"What is the new collection?"**.

## The Ecosystem Diagram

This diagram provides a high-level overview of the entire ecosystem, showing the tools within each pillar and their progression from simple to powerful.

```
                                      +-------------------------+
                                      |   The `dot` Ecosystem   |
                                      +-------------------------+
                                                 |
                    +----------------------------+----------------------------+
                    |                            |                            |
        +-----------v-----------+    +-----------v-----------+    +-----------v-----------+
        |  Pillar 1: Addressing |    |    Pillar 2: Logic    |    |  Pillar 3: Transform  |
        |        (Depth)        |    |       (Truth)         |    |      (Shape)          |
        | "Where is the data?"  |    |  "Is this true?"      |    | "How does it change?" |
        +-----------------------+    +-----------------------+    +-----------------------+
                    |                            |                            |
        Simple:   `dotget`                  `dotexists`                 `dotpluck` (doc→any)
                    |                            |                            |
        Patterns: `dotstar`                  `dotequals`                  +-------------------+
                    |                            |                        |                   |
        Advanced: `dotselect`              `dotany`/`dotall`        `dotmod` (doc→doc)   `dotpipe` (doc→any)
                    |                            |                        |                   |
        Engine:   `dotpath`                  `dotquery`              `dotbatch` (batch/txn)
```

### Pillar 1: The Addressing Pillar (Depth)

This pillar focuses on finding and extracting data from within a single document.

1.  **`dotget` (Simple):** The entry point. Extracts a value from a single, exact path.
2.  **`dotstar` (Patterns):** Introduces wildcards (`*`) to find multiple values.
3.  **`dotselect` (Advanced):** The workhorse. Uses the full `dotpath` engine to perform complex selections with filters, slices, and descendants.
4.  **`dotpath` (Engine):** The underlying path-parsing and resolution engine that is extensible and compositional, allowing for custom path segments and logic. The simpler operations (`dotget`, `dotstar`, `dotselect`) should not be built on top of `dotpath`, but implemented as simply as possible to avoid unnecessary complexity. However, conceptually, `dotpath` is the "Turing-complete" addressing engine of the ecosystem, allowing for arbitrary path expressions and logic.

### Pillar 2: The Logic Pillar (Truth)

This pillar focuses on asking true/false questions about a single document.

1.  **`dotexists` (Simple Structure):** The simplest question: does a path exist at all?

2.  **`dotequals` (Simple Content):** If a path exists, does it have a particular value?
3.  **`dotany`/`dotall` (Quantifiers):** The bridge to complexity. Applies a simple condition to multiple values found by a `dotstar` path.
4.  **`dotquery` (Engine):** The complete logic engine. Allows for building complex, compositional queries with AND/OR/NOT logic.

### Pillar 3: The Transformation Pillar (Shape)

This pillar focuses on transforming the *shape* of a single document, answering **"How does it change?"**. All operations are immutable and compositional.

- **`dotpluck` (Simple):** Extracts zero or more values from a document. If the path is exact, returns a single value or none; if the path includes wildcards, returns a list of all matches.
- **`dotmod` (Surgical):** Performs a targeted, immutable modification to a document (e.g., set, delete, or update a value at a path). Designed for simple, direct edits—easy for common cases, but limited in scope.
- **`dotpipe` (Compositional):** Composes multiple transformations, allowing for arbitrary mapping, restructuring, and function composition over a document. More general and powerful, but sometimes less ergonomic for simple edits than `dotmod`. All transformations can be piped, but `dotmod` and `dotpipe` are side-by-side: each is best for different user needs.
- **`dotbatch` (Transactional):** Applies a batch of modifications as a single transaction, enabling all-or-nothing guarantees and complex, multi-step updates. `dotbatch` can leverage both `dotmod` and `dotpipe` operations, and may support advanced features like rollback, validation, or atomicity.

---

## Collections: Lifting the Pillars to Streams

The Collections layer extends the three pillars from single documents to *streams* or *sets* of documents (e.g., JSONL). It is divided into two wings:

```
+-----------------------------+
|   Collections (Breadth)     |
+-----------------------------+
           |
   +-------+--------+
   |                |
Boolean Wing   Transforming Wing
 (Filtering)      (Mapping/Relating)
   |                |
   |                |
   v                v
`dothas`        (dotmod, dotpipe, dotbatch, dotpluck, ...)
`dotfind`           |
`dotfilter`         |
                    |
                `dotrelate` (multi-collection, highest abstraction)
```

- The **Boolean Wing** is essential for collections: filtering, searching, and logical operations over sets of documents. Boolean algebra on collections is homomorphic to boolean logic on queries: e.g., the intersection of subsets x₁ and x₂ (from queries q₁ and q₂) is the same as applying (q₁ AND q₂) to the original collection.
- The **Transforming Wing** includes repeated application of single-document transforms (dotmod, dotpipe, dotbatch, dotpluck, etc.), but the highest-level operation is **dotrelate**, which operates over multiple collections and enables relational algebra (joins, unions, etc.).
- `dotpipe` in collections is analogous to a "docview"—a new way of viewing or mapping your documents, but true database-style views and set operations are the domain of `dotrelate`.
- `dotbatch` at the collection level enables transactional or efficient batch operations across the entire set.

---

## Summary Table

| Pillar         | Single Document (Depth/Truth/Shape) | Collections (Breadth)         |
|--------------- |-------------------------------------|-------------------------------|
| Addressing     | dotget, dotstar, dotselect, dotpath | dotfind, dothas               |
| Logic          | dotequals, dotexists, dotany, dotall, dotquery | dotfilter           |
| Transform      | dotpluck, dotmod, dotpipe, dotbatch | dotpluck, dotmod, dotpipe, dotbatch, dotrelate |

---

## Design Principles

- **Compositionality:** All operations can be composed, both within and across pillars.
- **Immutability:** All transformations are immutable; original data is never mutated.
- **Pedagogical Progression:** Each pillar and wing is organized from simple to advanced, making the ecosystem approachable for beginners and powerful for experts.
- **Lifting:** The collections layer is a lifting of the single-document pillars to operate over streams/sets, preserving the same semantics and compositionality.

---

By adopting this formal structure, the `dot` ecosystem provides a highly consistent, predictable, and teachable set of tools for both single-document and collection-oriented data manipulation.
