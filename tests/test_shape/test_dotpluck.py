"""
Tests for dotpluck - Shape pillar primitive for reshaping data.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from shape.dotpluck.core import pluck, pluck_simple, pluck_subset, pluck_list


class TestPluck:
    """Test the main pluck function for reshaping data."""
    
    def test_pluck_flat_shape(self):
        """Test basic flat reshaping."""
        data = {"user": {"firstName": "Alice", "age": 30}}
        shape = {"name": "user.firstName", "years": "user.age"}
        result = pluck(data, shape)
        assert result == {"name": "Alice", "years": 30}
    
    def test_pluck_nested_shape(self):
        """Test nested reshaping."""
        data = {
            "user": {"firstName": "Alice", "lastName": "Smith", "age": 30},
            "settings": {"theme": "dark", "lang": "en"}
        }
        shape = {
            "person": {
                "first": "user.firstName",
                "last": "user.lastName"
            },
            "prefs": {
                "display": "settings.theme"
            }
        }
        result = pluck(data, shape)
        assert result == {
            "person": {"first": "Alice", "last": "Smith"},
            "prefs": {"display": "dark"}
        }
    
    def test_pluck_with_static_values(self):
        """Test reshaping with static values mixed in."""
        data = {"user": {"name": "Alice"}}
        shape = {
            "name": "user.name",  # Path to extract
            "version": 1.0,       # Static float (non-string)
            "active": True,       # Static boolean
            "count": 42           # Static integer
        }
        result = pluck(data, shape)
        assert result == {"name": "Alice", "version": 1.0, "active": True, "count": 42}
    
    def test_pluck_missing_paths(self):
        """Test handling of missing paths."""
        data = {"user": {"name": "Alice"}}
        shape = {"name": "user.name", "email": "user.email", "age": "user.age"}
        result = pluck(data, shape)
        assert result == {"name": "Alice", "email": None, "age": None}
    
    def test_pluck_from_list(self):
        """Test plucking from list indices."""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        shape = {
            "first_user": "users.0.name",
            "second_user": "users.1.name"
        }
        result = pluck(data, shape)
        assert result == {"first_user": "Alice", "second_user": "Bob"}
    
    def test_pluck_non_dict_shape(self):
        """Test that non-dict shapes return as-is."""
        data = {"value": 42}
        assert pluck(data, "hello") == "hello"
        assert pluck(data, 123) == 123
        assert pluck(data, None) == None


class TestPluckSimple:
    """Test the pluck_simple convenience function."""
    
    def test_pluck_simple_basic(self):
        """Test simple flat projection."""
        data = {"user": {"firstName": "Alice", "years": 30}}
        result = pluck_simple(data, name="user.firstName", age="user.years")
        assert result == {"name": "Alice", "age": 30}
    
    def test_pluck_simple_with_missing(self):
        """Test simple projection with missing paths."""
        data = {"user": {"firstName": "Alice"}}
        result = pluck_simple(data, name="user.firstName", email="user.email")
        assert result == {"name": "Alice", "email": None}
    
    def test_pluck_simple_rename_fields(self):
        """Test field renaming during projection."""
        data = {
            "product": {
                "product_name": "Widget",
                "product_price": 29.99,
                "product_category": "tools"
            }
        }
        result = pluck_simple(
            data,
            name="product.product_name",
            price="product.product_price",
            category="product.product_category"
        )
        assert result == {"name": "Widget", "price": 29.99, "category": "tools"}


class TestPluckSubset:
    """Test the pluck_subset function for field subsetting."""
    
    def test_pluck_subset_basic(self):
        """Test basic field subsetting."""
        data = {"user": {"name": "Alice", "age": 30, "email": "alice@example.com"}}
        result = pluck_subset(data, "user", "name", "email")
        assert result == {"name": "Alice", "email": "alice@example.com"}
    
    def test_pluck_subset_exclude_fields(self):
        """Test excluding sensitive fields."""
        data = {"user": {"id": 1, "name": "Alice", "password": "secret", "email": "alice@example.com"}}
        result = pluck_subset(data, "user", "id", "name", "email")
        assert result == {"id": 1, "name": "Alice", "email": "alice@example.com"}
        assert "password" not in result
    
    def test_pluck_subset_missing_base_path(self):
        """Test subsetting with missing base path."""
        data = {"company": {"name": "TechCorp"}}
        result = pluck_subset(data, "user", "name", "email")
        assert result == {}
    
    def test_pluck_subset_non_dict_base(self):
        """Test subsetting when base is not a dict."""
        data = {"items": ["a", "b", "c"]}
        result = pluck_subset(data, "items", "name")
        assert result == {}
    
    def test_pluck_subset_with_nonexistent_keys(self):
        """Test subsetting with keys that don't exist."""
        data = {"user": {"name": "Alice", "age": 30}}
        result = pluck_subset(data, "user", "name", "email", "phone")
        assert result == {"name": "Alice"}


class TestPluckList:
    """Test the pluck_list function for extracting values as a list."""
    
    def test_pluck_list_single_value(self):
        """Test extracting a single value as list."""
        data = {"user": {"name": "Alice"}}
        assert pluck_list(data, "user.name") == ["Alice"]
    
    def test_pluck_list_multiple_values(self):
        """Test extracting multiple values."""
        data = {"user": {"name": "Alice", "age": 30}}
        assert pluck_list(data, "user.name", "user.age") == ["Alice", 30]
    
    def test_pluck_list_missing_path(self):
        """Test list extraction with missing paths."""
        data = {"user": {"name": "Alice"}}
        assert pluck_list(data, "user.name", "user.email") == ["Alice", None]
    
    def test_pluck_list_nested_paths(self):
        """Test list extraction from nested paths."""
        data = {
            "company": {
                "name": "TechCorp",
                "ceo": {"name": "Bob", "age": 45}
            }
        }
        result = pluck_list(data, "company.name", "company.ceo.name", "company.ceo.age")
        assert result == ["TechCorp", "Bob", 45]
    
    def test_pluck_list_from_arrays(self):
        """Test list extraction from array indices."""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        assert pluck_list(data, "users.0.name", "users.1.name") == ["Alice", "Bob"]
    
    def test_pluck_list_empty_paths(self):
        """Test list extraction with no paths."""
        data = {"a": 1}
        assert pluck_list(data) == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])