"""
Tests for dotfilter - Collections boolean algebra for document filtering.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/collections'))

from dotfilter.core import (
    QuerySet,
    filter_docs,
    filter_by_path,
    filter_by_existence,
    combine_filters
)


class TestFilterDocs:
    """Test the simple filter_docs function."""
    
    def test_filter_docs_basic(self):
        docs = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 17},
            {"name": "Charlie", "age": 25}
        ]
        result = filter_docs(docs, lambda d: d["age"] >= 18)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Charlie"
    
    def test_filter_docs_empty_list(self):
        assert filter_docs([], lambda d: True) == []
    
    def test_filter_docs_none_match(self):
        docs = [{"value": 1}, {"value": 2}]
        assert filter_docs(docs, lambda d: d["value"] > 10) == []
    
    def test_filter_docs_all_match(self):
        docs = [{"value": 1}, {"value": 2}]
        result = filter_docs(docs, lambda d: d["value"] > 0)
        assert len(result) == 2


class TestFilterByPath:
    """Test the filter_by_path function."""
    
    def test_filter_by_path_simple(self):
        docs = [
            {"status": "active"},
            {"status": "inactive"},
            {"status": "active"}
        ]
        result = filter_by_path(docs, "status", "active")
        assert len(result) == 2
    
    def test_filter_by_path_nested(self):
        docs = [
            {"user": {"role": "admin"}},
            {"user": {"role": "user"}},
            {"user": {"role": "admin"}}
        ]
        result = filter_by_path(docs, "user.role", "admin")
        assert len(result) == 2
    
    def test_filter_by_path_missing(self):
        docs = [
            {"name": "Alice"},
            {"name": "Bob", "role": "admin"}
        ]
        result = filter_by_path(docs, "role", "admin")
        assert len(result) == 1
        assert result[0]["name"] == "Bob"


class TestFilterByExistence:
    """Test the filter_by_existence function."""
    
    def test_filter_by_existence_basic(self):
        docs = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob"},
            {"name": "Charlie", "email": "charlie@example.com"}
        ]
        result = filter_by_existence(docs, "email")
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Charlie"
    
    def test_filter_by_existence_nested(self):
        docs = [
            {"user": {"profile": {"bio": "Hello"}}},
            {"user": {"profile": {}}},
            {"user": {}}
        ]
        result = filter_by_existence(docs, "user.profile.bio")
        assert len(result) == 1


class TestCombineFilters:
    """Test the combine_filters function."""
    
    def test_combine_filters_and(self):
        docs = [
            {"age": 30, "role": "admin"},
            {"age": 17, "role": "admin"},
            {"age": 25, "role": "user"}
        ]
        result = combine_filters(
            docs,
            lambda d: d["age"] >= 18,
            lambda d: d["role"] == "admin",
            mode="and"
        )
        assert len(result) == 1
        assert result[0]["age"] == 30
    
    def test_combine_filters_or(self):
        docs = [
            {"age": 30, "role": "admin"},
            {"age": 17, "role": "admin"},
            {"age": 25, "role": "user"}
        ]
        result = combine_filters(
            docs,
            lambda d: d["age"] >= 30,
            lambda d: d["role"] == "admin",
            mode="or"
        )
        assert len(result) == 2  # age 30 OR role admin
    
    def test_combine_filters_invalid_mode(self):
        with pytest.raises(ValueError, match="Invalid mode"):
            combine_filters([], lambda d: True, mode="xor")


class TestQuerySet:
    """Test the QuerySet class for lazy evaluation."""
    
    def test_queryset_basic_filter(self):
        docs = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 17},
            {"name": "Charlie", "age": 25}
        ]
        qs = QuerySet(docs).filter(lambda d: d["age"] >= 18)
        result = qs.list()
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
    
    def test_queryset_chained_filters(self):
        docs = [
            {"name": "Alice", "age": 30, "role": "admin"},
            {"name": "Bob", "age": 25, "role": "user"},
            {"name": "Charlie", "age": 35, "role": "admin"}
        ]
        qs = QuerySet(docs).filter(lambda d: d["age"] >= 25).filter(lambda d: d["role"] == "admin")
        result = qs.list()
        assert len(result) == 2
        assert all(d["role"] == "admin" and d["age"] >= 25 for d in result)
    
    def test_queryset_exclude(self):
        docs = [
            {"name": "Alice", "status": "active"},
            {"name": "Bob", "status": "inactive"},
            {"name": "Charlie", "status": "active"}
        ]
        qs = QuerySet(docs).exclude(lambda d: d["status"] == "inactive")
        result = qs.list()
        assert len(result) == 2
        assert all(d["status"] == "active" for d in result)
    
    def test_queryset_union(self):
        # Use same object references to test deduplication
        doc1, doc2, doc3 = {"id": 1}, {"id": 2}, {"id": 3}
        docs1 = [doc1, doc2]
        docs2 = [doc2, doc3]  # doc2 is shared
        qs1 = QuerySet(docs1)
        qs2 = QuerySet(docs2)
        result = (qs1 | qs2).list()
        assert len(result) == 3  # Union should deduplicate doc2
    
    def test_queryset_intersection(self):
        docs = [
            {"id": 1, "type": "A"},
            {"id": 2, "type": "B"},
            {"id": 3, "type": "A"}
        ]
        qs1 = QuerySet(docs).filter(lambda d: d["id"] <= 2)
        qs2 = QuerySet(docs).filter(lambda d: d["type"] == "A")
        result = (qs1 & qs2).list()
        assert len(result) == 1
        assert result[0]["id"] == 1
    
    def test_queryset_difference(self):
        docs = [{"id": 1}, {"id": 2}, {"id": 3}]
        qs1 = QuerySet(docs).filter(lambda d: d["id"] <= 2)
        qs2 = QuerySet(docs).filter(lambda d: d["id"] == 1)
        result = (qs1 - qs2).list()
        assert len(result) == 1
        assert result[0]["id"] == 2
    
    def test_queryset_count(self):
        docs = [{"value": i} for i in range(10)]
        qs = QuerySet(docs).filter(lambda d: d["value"] >= 5)
        assert qs.count() == 5
    
    def test_queryset_exists(self):
        docs = [{"value": 1}, {"value": 2}]
        assert QuerySet(docs).filter(lambda d: d["value"] > 0).exists() is True
        assert QuerySet(docs).filter(lambda d: d["value"] > 10).exists() is False
    
    def test_queryset_first(self):
        docs = [{"id": 1}, {"id": 2}, {"id": 3}]
        first = QuerySet(docs).filter(lambda d: d["id"] > 1).first()
        assert first["id"] == 2
        
        none = QuerySet(docs).filter(lambda d: d["id"] > 10).first()
        assert none is None
    
    def test_queryset_lazy_evaluation(self):
        """Test that QuerySet is truly lazy."""
        call_count = 0
        
        def counting_filter(d):
            nonlocal call_count
            call_count += 1
            return d["value"] > 5
        
        docs = [{"value": i} for i in range(10)]
        qs = QuerySet(docs).filter(counting_filter)
        
        # Filter shouldn't be called yet
        assert call_count == 0
        
        # Now force evaluation
        result = qs.list()
        assert call_count == 10  # Filter called for each document
        assert len(result) == 4  # Values 6, 7, 8, 9


class TestComplexScenarios:
    """Test complex real-world filtering scenarios."""
    
    def test_user_filtering_scenario(self):
        users = [
            {"name": "Alice", "age": 30, "role": "admin", "active": True},
            {"name": "Bob", "age": 17, "role": "user", "active": True},
            {"name": "Charlie", "age": 25, "role": "user", "active": False},
            {"name": "David", "age": 35, "role": "admin", "active": True}
        ]
        
        # Find active adult admins
        qs = QuerySet(users).filter(
            lambda u: u["age"] >= 18
        ).filter(
            lambda u: u["role"] == "admin"
        ).filter(
            lambda u: u["active"]
        )
        
        result = qs.list()
        assert len(result) == 2
        assert all(u["role"] == "admin" and u["age"] >= 18 and u["active"] for u in result)
    
    def test_product_filtering_scenario(self):
        products = [
            {"name": "Widget", "price": 29.99, "category": "tools", "in_stock": True},
            {"name": "Gadget", "price": 49.99, "category": "electronics", "in_stock": False},
            {"name": "Doohickey", "price": 19.99, "category": "tools", "in_stock": True},
            {"name": "Thingamajig", "price": 99.99, "category": "electronics", "in_stock": True}
        ]
        
        # Find affordable in-stock tools OR expensive electronics
        tools = QuerySet(products).filter(
            lambda p: p["category"] == "tools"
        ).filter(
            lambda p: p["price"] < 50
        ).filter(
            lambda p: p["in_stock"]
        )
        
        electronics = QuerySet(products).filter(
            lambda p: p["category"] == "electronics"
        ).filter(
            lambda p: p["price"] > 50
        )
        
        result = (tools | electronics).list()
        assert len(result) == 3
        names = [p["name"] for p in result]
        assert "Widget" in names
        assert "Doohickey" in names
        assert "Thingamajig" in names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])