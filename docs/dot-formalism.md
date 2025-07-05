# The `dot` Ecosystem — A Formal Blueprint

> **Premise.** Manipulating semi-structured data is easiest when every operation answers exactly one question and composes cleanly with every other operation.
> **Goal.** Provide a minimal yet complete algebra for JSON-like documents and their collections, with clear pedagogical on-ramps.
> **Method.** Factor the problem space into three orthogonal *pillars* (Depth ≈ Addressing, Truth ≈ Logic, Shape ≈ Transformation) and *lift* them from single documents to collections.

---

## 1 The Three Pillars

| Pillar    | Core Question                         | Domain   | Codomain    | Primitive       |
| --------- | ------------------------------------- | -------- | ----------- | --------------- |
| **Depth** | “*Where* is the data?”                | Document | Path ↦ 𝑉\* | **`dotget`**    |
| **Truth** | “*Is* this assertion true here?”      | Document | 𝔹          | **`dotexists`** |
| **Shape** | “*How* should the data be re-shaped?” | Document | Document    | **`dotpluck`**  |

*Notation.* A JSON document is an element of $\mathcal D$. A *path* is a finite sequence of selectors; evaluation yields either a single value or a multiset $V^{*}$ (to accommodate wildcards). Boolean results live in $\mathbb B=\{\bot,\top\}$.

### 1.1 Depth — Addressing Algebra

| Layer     | Operator    | Semantic Type                                                            | Observations                                   |
| --------- | ----------- | ------------------------------------------------------------------------ | ---------------------------------------------- |
| entry     | `dotget`    | $\mathcal D \times \text{Path}_{\text{exact}}\to V\cup\{\emptyset\}$     | Total if we treat “missing” as $\emptyset$.    |
| pattern   | `dotstar`   | $\mathcal D \times \text{Path}_{*} \to V^{*}$                            | Wildcards induce *Kleene-star* expansion.      |
| workhorse | `dotselect` | $\mathcal D \times \text{Path}_{\text{expr}} \to V^{*}$                  | Admits slices, filters ↔ regular-path queries. |
| engine    | `dotpath`   | Free **algebra** on selectors; Turing-complete by user-defined reducers. |                                                |

> **Formally** each operator is a *morphism* in the Kleisli category of the powerset monad, ensuring compositionality: `dotstar` ∘ `dotselect` → still a set of values.

### 1.2 Truth — Predicate Calculus

| Layer       | Operator            | Type                                              | Law                                                                                             |
| ----------- | ------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| structure   | `dotexists`         | $\mathcal D \times P \to 𝔹$                      | `exists(p)` ≡ `count(dotstar(p)) > 0`.                                                          |
| content     | `dotequals`         | $\mathcal D \times (P,V) \to 𝔹$                  | Reflexive, symmetric only on singleton paths.                                                   |
| quantifiers | `dotany` / `dotall` | $\mathcal D \times (P, φ) \to 𝔹$                 | Lift predicate $φ$ point-wise then aggregate with ∨ / ∧.                                        |
| engine      | `dotquery`          | $\mathcal D \times \mathcal L_{BOOL}(φ_i) \to 𝔹$ | $\mathcal L_{BOOL}$ is propositional logic; distributive laws preserve short-circuit semantics. |

> **Boolean algebra closure.** Predicates form a Boolean algebra under ∧, ∨, ¬ that is *homomorphic* to set algebra on result subsets (intersection, union, complement).

### 1.3 Shape — Endofunctors on $\mathcal D$

| Layer         | Operator   | Type                                             | Category-theoretic view                                           |
| ------------- | ---------- | ------------------------------------------------ | ----------------------------------------------------------------- |
| extract       | `dotpluck` | $\mathcal D \times P \to V^{*}$                  | Not a transform; a *projection* functor to Sets.                  |
| surgical      | `dotmod`   | $\mathcal D \times δ \to \mathcal D$             | δ = {insert, update, delete}. *Lens* with put-get law.            |
| compositional | `dotpipe`  | $\mathcal D \times F^{*} \to \mathcal D$         | Kleisli composition of pure functions $F: \mathcal D→\mathcal D$. |
| transactional | `dotbatch` | $\mathcal D^{*} \times Δ^{*} \to \mathcal D^{*}$ | *Monoid* action; supports ACID if Δ is sequence-serialisable.     |

---

## 2 Lifting to Collections

Let a *collection* be a finite multiset $C \subseteq \mathcal D$. Operations lift via:

$$
\operatorname{map} : (\mathcal D \to X) \to (C \to X^{*}) \qquad
\operatorname{filter} : (\mathcal D \to 𝔹) \to (C \to C)
$$

### 2.1 Boolean Wing (Filtering)

| Operator    | Definition                                        | Note                                                  |
| ----------- | ------------------------------------------------- | ----------------------------------------------------- |
| `dothas`    | $C, P \mapsto \{d∈C \mid \text{dotexists}(d,P)\}$ | Primitive filter.                                     |
| `dotfind`   | $C, φ \mapsto \{d∈C \mid φ(d)\}$                  | `φ` any Truth-pillar predicate.                       |
| `dotfilter` | Higher-order: accepts combinators (AND/OR/NOT).   | Closure under Boolean algebra proven by homomorphism. |

### 2.2 Transforming Wing (Mapping & Relating)

| Operator                                    | Lifted From  | Semantics                                                                                     |
| ------------------------------------------- | ------------ | --------------------------------------------------------------------------------------------- |
| `dotmod`, `dotpipe`, `dotbatch`, `dotpluck` | Shape pillar | Point-wise map; distributive over union.                                                      |
| `dotrelate`                                 | *new*        | Binary relation $C_1 \Join C_2 \to C_{12}$; isomorphic to relational algebra (σ, π, ⋈, ∪, −). |

> **Key guarantee.** Every collection operator is a *monoid homomorphism* w\.r.t. multiset union, enabling parallelisation and streaming.

---

## 3 Pedagogical Gradient

1. **Hello-World phase.** `dotget`, `dotexists`, `dotpluck` —  O(1) mental load.
2. **Pattern phase.** Add `dotstar`, `dotequals`, `dotmod`.
3. **Power-user phase.** `dotselect`, `dotany/all`, `dotpipe`.
4. **Expert / DSL author.** `dotpath`, `dotquery`, `dotbatch`, `dotrelate`.

Each stage is *conservative*: every new construct can be desugared into earlier ones plus a small kernel, preserving learnability.

---

## 4 Design Invariants

* **Purity & Immutability.** Functions are referentially transparent; concurrency is trivial.
* **Totality by Convention.** Missing paths yield $\emptyset$ rather than exceptions, pushing error handling into the type.
* **Compositionality.** Operators form algebras (Boolean, monoidal, Kleisli) guaranteeing that *compose ⇒ reason locally*.
* **Orthogonality.** No operator belongs to more than one pillar; cross-cutting concerns are expresses as functor lifts, not ad-hoc features.
* **Extensibility.** Users can register new selector primitives or predicates; completion is measured against algebraic closure, not feature lists.

---

## 5 Big-Picture Fit

* `dot`’s **Depth–Truth–Shape** triad mirrors the **CRUD** partition (Read, Validate, Update).
* The collection lift embeds seamlessly into stream processors (e.g., UNIX pipes, Apache Beam) because all lifted ops are monoid homomorphisms.
* Advanced users can harvest **category-theoretic** intuition: paths are *optics*, predicates are *subobjects*, transforms are *endofunctors*.
* The architecture matches database theory: single-document logic ≈ tuple calculus; `dotrelate` ≈ relational algebra; streaming lift ≈ data-parallel query plans.

---

## 6 Next Questions (Skeptical Checklist)

1. **Can every JSONPath feature be expressed in `dotpath` without semantic leaks?**
2. **Are `dotbatch` rollbacks composable with streaming sinks?**
3. **Which algebraic laws break under heterogeneous array mixes, and do we care?**
4. **How do we reconcile user-defined side-effectful functions with purity guarantees?**
5. **Can the type system (e.g., gradual typing) enforce pillar boundaries statically?**

---

### TL;DR

`dot` is not a toolbox; it is a **small, law-governed algebra** for interrogating and reshaping data.
Three orthogonal pillars give you location, truth, and transformation; functorial lifting scales them to streams. Everything else is just syntax sugar.
-------------------------------------------------------------------------------------------------------

let's think very carefully about how to improve  our documents with this formalism. we can also read from proposal-collections-pillar.md for ideas.