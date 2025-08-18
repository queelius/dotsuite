"""
dotfilter - Boolean algebra on document collections.

This lifts Truth pillar operations to work on collections of documents.
Provides lazy evaluation and set operations (union, intersection, difference).

The key insight: Boolean algebra on collections is homomorphic to boolean logic 
on queries. The intersection of results from queries q₁ and q₂ is the same as 
applying (q₁ AND q₂) to the original collection.
"""

from typing import Any, Callable, Iterator, List, Union, Optional


class QuerySet:
    """
    A lazy, composable query set for filtering document collections.
    
    Inspired by Django's ORM QuerySet, but for arbitrary JSON-like documents.
    Operations are lazy - filtering only happens when results are materialized.
    """
    
    def __init__(self, documents: Union[List[Any], Iterator[Any]], filters: Optional[List[Callable]] = None):
        """
        Initialize a QuerySet.
        
        Args:
            documents: Collection of documents (list or iterator)
            filters: List of filter functions to apply (internal use)
        """
        self._documents = documents
        self._filters = filters or []
        self._evaluated = False
        self._cache = None
    
    def filter(self, predicate: Callable[[Any], bool]) -> 'QuerySet':
        """
        Filter documents by a predicate (lazy).
        
        Args:
            predicate: Function that returns True for documents to keep
            
        Returns:
            New QuerySet with additional filter
            
        Examples:
            >>> qs = QuerySet(users).filter(lambda u: u['age'] > 18)
        """
        return QuerySet(self._documents, self._filters + [predicate])
    
    def exclude(self, predicate: Callable[[Any], bool]) -> 'QuerySet':
        """
        Exclude documents matching a predicate (lazy).
        
        Args:
            predicate: Function that returns True for documents to exclude
            
        Returns:
            New QuerySet with exclusion filter
        """
        return self.filter(lambda doc: not predicate(doc))
    
    def union(self, other: 'QuerySet') -> 'QuerySet':
        """
        Union of two QuerySets (lazy).
        
        Set operation: self ∪ other
        """
        def generator():
            seen = set()
            for doc in self:
                doc_id = id(doc)  # Use object identity for deduplication
                if doc_id not in seen:
                    seen.add(doc_id)
                    yield doc
            for doc in other:
                doc_id = id(doc)
                if doc_id not in seen:
                    seen.add(doc_id)
                    yield doc
        
        return QuerySet(generator())
    
    def intersect(self, other: 'QuerySet') -> 'QuerySet':
        """
        Intersection of two QuerySets (lazy).
        
        Set operation: self ∩ other
        """
        # Materialize other for membership testing
        other_set = set(id(doc) for doc in other)
        return self.filter(lambda doc: id(doc) in other_set)
    
    def difference(self, other: 'QuerySet') -> 'QuerySet':
        """
        Difference of two QuerySets (lazy).
        
        Set operation: self - other
        """
        # Materialize other for membership testing
        other_set = set(id(doc) for doc in other)
        return self.filter(lambda doc: id(doc) not in other_set)
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate over filtered documents."""
        if self._evaluated and self._cache is not None:
            yield from self._cache
        else:
            # Apply all filters
            docs = self._documents
            for filter_fn in self._filters:
                docs = filter(filter_fn, docs)
            
            # Cache results if we're iterating
            if not self._evaluated:
                self._cache = []
                for doc in docs:
                    self._cache.append(doc)
                    yield doc
                self._evaluated = True
            else:
                yield from docs
    
    def __or__(self, other: 'QuerySet') -> 'QuerySet':
        """Union using | operator."""
        return self.union(other)
    
    def __and__(self, other: 'QuerySet') -> 'QuerySet':
        """Intersection using & operator."""
        return self.intersect(other)
    
    def __sub__(self, other: 'QuerySet') -> 'QuerySet':
        """Difference using - operator."""
        return self.difference(other)
    
    def count(self) -> int:
        """Count matching documents."""
        return sum(1 for _ in self)
    
    def exists(self) -> bool:
        """Check if any documents match."""
        try:
            next(iter(self))
            return True
        except StopIteration:
            return False
    
    def first(self) -> Optional[Any]:
        """Get the first matching document."""
        try:
            return next(iter(self))
        except StopIteration:
            return None
    
    def list(self) -> List[Any]:
        """Materialize to a list."""
        return list(self)


def filter_docs(documents: List[Any], predicate: Callable[[Any], bool]) -> List[Any]:
    """
    Simple functional filter for document collections.
    
    Args:
        documents: List of documents
        predicate: Function that returns True for documents to keep
        
    Returns:
        List of filtered documents
        
    Examples:
        >>> users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 17}]
        >>> filter_docs(users, lambda u: u['age'] >= 18)
        [{"name": "Alice", "age": 30}]
    """
    return list(filter(predicate, documents))


def filter_by_path(documents: List[Any], path: str, value: Any) -> List[Any]:
    """
    Filter documents where a path equals a specific value.
    
    Args:
        documents: List of documents
        path: Dot-notation path
        value: Expected value
        
    Returns:
        List of documents where path equals value
        
    Examples:
        >>> users = [{"name": "Alice", "role": "admin"}, {"name": "Bob", "role": "user"}]
        >>> filter_by_path(users, "role", "admin")
        [{"name": "Alice", "role": "admin"}]
    """
    from truth.dotequals.core import equals
    return filter_docs(documents, lambda doc: equals(doc, path, value))


def filter_by_existence(documents: List[Any], path: str) -> List[Any]:
    """
    Filter documents where a path exists.
    
    Args:
        documents: List of documents
        path: Dot-notation path
        
    Returns:
        List of documents where path exists
    """
    from truth.dotexists.core import check
    return filter_docs(documents, lambda doc: check(doc, path))


def combine_filters(documents: List[Any], *predicates: Callable[[Any], bool], mode: str = "and") -> List[Any]:
    """
    Combine multiple filter predicates with AND or OR logic.
    
    Args:
        documents: List of documents
        *predicates: Filter functions
        mode: "and" or "or" - how to combine predicates
        
    Returns:
        List of filtered documents
    """
    if mode == "and":
        combiner = all
    elif mode == "or":
        combiner = any
    else:
        raise ValueError(f"Invalid mode: {mode}. Use 'and' or 'or'.")
    
    return filter_docs(documents, lambda doc: combiner(p(doc) for p in predicates))