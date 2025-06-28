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
        |  Pillar 1: Addressing |    |    Pillar 2: Logic    |    | Pillar 3: Collections |
        |        (Depth)        |    |        (Truth)        |    |        (Breadth)      |
        | "Where is the data?"  |    |    "Is this true?"    |    |  "What about the set?"|
        +-----------------------+    +-----------------------+    +-----------------------+
                    |                            |                            |
        Simple:   `dotget`                   `dotequals`                      |
                    |                            |                            |
        Structure:  |                        `dotexists`              +-------+-----------+
                    |                            |                    |                   |
        Patterns: `dotstar`                      |            +-------v-------+   +-------v---------+
                    |                            |            | Boolean Wing  |   | Transforming    |
        Quantifiers:|                        `dotany`/`dotall`|  (Filtering)  |   | Wing (Reshaping)|
                    |                            |            +---------------+   +-----------------+
        Advanced: `dotselect`                    |                  `dotfind`           |
                    |                            |                  `dothas`            +------------+
        Engine:   `dotpath`                  `dotquery`             `dotfilter`         |            |
                                                                                +-----v---+    +-----v-----+
                                                                                | Mapping |    | Relating  |
                                                                                +---------+    +-----------+
                                                                                `dotpluck`     `dotrelate`
                                                                                `dotpipe`
```

## Pillar 1: The Addressing Pillar (Depth)

This pillar focuses on finding and extracting data from within a single document.

1.  **`dotget` (Simple):** The entry point. Extracts a value from a single, exact path.
2.  **`dotstar` (Patterns):** Introduces wildcards (`*`) to find multiple values.
3.  **`dotselect` (Advanced):** The workhorse. Uses the full `dotpath` engine to perform complex selections with filters, slices, and descendants.
4.  **`dotpath` (Engine):** The underlying path-parsing and resolution engine that powers the entire pillar.

## Pillar 2: The Logic Pillar (Truth)

This pillar focuses on asking true/false questions about a single document.

1.  **`dotequals` (Simple Content):** The simplest assertion. Checks if the value at an exact path equals a specific value.
2.  **`dotexists` (Simple Structure):** The second fundamental assertion. Checks if a path exists at all.
3.  **`dotany`/`dotall` (Quantifiers):** The bridge to complexity. Applies a simple condition to multiple values found by a `dotstar` path.
4.  **`dotquery` (Engine):** The complete logic engine. Allows for building complex, compositional queries with AND/OR/NOT logic.

## Pillar 3: The Collections Pillar (Breadth)

This new pillar is the focus of this proposal. It operates not on a single document, but on a stream of documents. It is divided into two wings that perform orthogonal operations.

### The Boolean Wing (Filtering)

This wing answers the question: **"Which documents should I keep?"** Its operations reduce the *size* of the collection without changing the *shape* of the documents within it.

1.  **`dotfind` (Simple):** The "dotget of collections." Finds the *first* document in a stream matching a specific key (e.g., `id: "user-123"`). It's a targeted lookup.
2.  **`dothas` (Structure):** The "dotexists of collections." Filters a stream, keeping only those documents that have a specific path.
3.  **`dotfilter` (Engine):** The "dotquery of collections." The most powerful tool. Filters a stream using a full `dotquery` expression, allowing for complex logical filtering.

### The Transforming Wing (Reshaping)

This wing answers the question: **"What do the new documents look like?"** Its operations change the *shape* of the documents, and may change the *size* of the collection. It contains two distinct, parallel strategies:

1.  **Mapping (Intra-Document Transformation):** This strategy transforms each document in isolation.
    *   **`dotpluck` (Simple):** The simplest map. Creates a new collection by extracting a single value from each document. It's a `projection`.
    *   **`dotpipe` (Engine):** The workhorse of mapping. Creates a new collection by applying a `dotpipe` template to each document, allowing for arbitrary and complex reshaping.

2.  **Relating (Inter-Document Transformation):** This strategy transforms the collection by operating on it as a complete set, often involving multiple collections.
    *   **`dotrelate` (Engine):** The full relational algebra engine. Performs complex, set-based operations that require knowledge of the entire collection(s), such as `join`, `union`, `intersect`, and `product`.

By adopting this formal structure, we create a highly consistent, predictable, and teachable ecosystem that can scale to solve a wide range of data manipulation problems.
