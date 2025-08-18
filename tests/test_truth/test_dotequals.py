"""
Tests for dotequals - Truth pillar pattern layer for value checking.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from truth.dotequals.core import equals, not_equals, equals_any, check


class TestEquals:
    """Test the equals function."""
    
    def test_equals_simple_value(self):
        data = {"status": "active"}
        assert equals(data, "status", "active") is True
        assert equals(data, "status", "inactive") is False
    
    def test_equals_nested_value(self):
        data = {"user": {"name": "Alice", "role": "admin"}}
        assert equals(data, "user.name", "Alice") is True
        assert equals(data, "user.role", "admin") is True
        assert equals(data, "user.name", "Bob") is False
    
    def test_equals_missing_path(self):
        data = {"user": {"name": "Alice"}}
        assert equals(data, "user.email", "alice@example.com") is False
        assert equals(data, "nonexistent.path", "anything") is False
    
    def test_equals_with_none(self):
        data = {"value": None}
        assert equals(data, "value", None) is True
        assert equals(data, "value", "something") is False
    
    def test_equals_with_numbers(self):
        data = {"count": 42, "price": 19.99}
        assert equals(data, "count", 42) is True
        assert equals(data, "price", 19.99) is True
        assert equals(data, "count", "42") is False  # Type matters
    
    def test_equals_with_lists(self):
        data = {"items": [1, 2, 3]}
        assert equals(data, "items", [1, 2, 3]) is True
        assert equals(data, "items", [1, 2]) is False
    
    def test_equals_list_element(self):
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        assert equals(data, "users.0.name", "Alice") is True
        assert equals(data, "users.1.name", "Bob") is True
    
    def test_check_alias(self):
        """Test that check is an alias for equals."""
        data = {"status": "active"}
        assert check(data, "status", "active") is True
        assert check is equals


class TestNotEquals:
    """Test the not_equals function."""
    
    def test_not_equals_basic(self):
        data = {"status": "active"}
        assert not_equals(data, "status", "inactive") is True
        assert not_equals(data, "status", "active") is False
    
    def test_not_equals_missing_path(self):
        data = {"user": {"name": "Alice"}}
        # Missing path returns None from dotget, so None != "anything" is True
        assert not_equals(data, "user.email", "anything") is True
        # But None == None, so missing path with None value is False
        assert not_equals(data, "user.email", None) is False
    
    def test_not_equals_with_none(self):
        data = {"value": None}
        assert not_equals(data, "value", "something") is True
        assert not_equals(data, "value", None) is False
    
    def test_not_equals_type_sensitive(self):
        data = {"count": 42}
        assert not_equals(data, "count", "42") is True  # Different types
        assert not_equals(data, "count", 43) is True
        assert not_equals(data, "count", 42) is False


class TestEqualsAny:
    """Test the equals_any function."""
    
    def test_equals_any_single_match(self):
        data = {"role": "admin"}
        assert equals_any(data, "role", "admin", "moderator", "user") is True
    
    def test_equals_any_no_match(self):
        data = {"role": "guest"}
        assert equals_any(data, "role", "admin", "moderator", "user") is False
    
    def test_equals_any_missing_path(self):
        data = {"user": {"name": "Alice"}}
        assert equals_any(data, "user.role", "admin", "user") is False
    
    def test_equals_any_with_mixed_types(self):
        data = {"value": 42}
        assert equals_any(data, "value", "42", 42, 43) is True
        assert equals_any(data, "value", "42", 43, None) is False
    
    def test_equals_any_empty_values(self):
        data = {"status": "active"}
        assert equals_any(data, "status") is False  # No values to match
    
    def test_equals_any_with_lists(self):
        data = {"tags": ["python", "testing"]}
        assert equals_any(
            data, "tags",
            ["python", "testing"],
            ["python"],
            ["testing"]
        ) is True


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_deeply_nested_path(self):
        data = {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        assert equals(data, "a.b.c.d.e", "deep") is True
    
    def test_numeric_string_keys(self):
        data = {"123": {"456": "value"}}
        assert equals(data, "123.456", "value") is True
    
    def test_boolean_values(self):
        data = {"active": True, "archived": False}
        assert equals(data, "active", True) is True
        assert equals(data, "archived", False) is True
        assert not_equals(data, "active", False) is True
    
    def test_empty_string_value(self):
        data = {"name": ""}
        assert equals(data, "name", "") is True
        assert not_equals(data, "name", "something") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])