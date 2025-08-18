"""
Tests for dotget - Depth pillar primitive for simple path navigation.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from depth.dotget.core import get


class TestBasicGet:
    """Test basic get functionality."""
    
    def test_get_simple_key(self):
        """Test getting a simple top-level key."""
        data = {"name": "Alice", "age": 30}
        assert get(data, "name") == "Alice"
        assert get(data, "age") == 30
    
    def test_get_nested_key(self):
        """Test getting nested keys."""
        data = {"user": {"name": "Alice", "age": 30}}
        assert get(data, "user.name") == "Alice"
        assert get(data, "user.age") == 30
    
    def test_get_deeply_nested(self):
        """Test getting deeply nested keys."""
        data = {
            "company": {
                "department": {
                    "team": {
                        "lead": "Alice"
                    }
                }
            }
        }
        assert get(data, "company.department.team.lead") == "Alice"
    
    def test_get_missing_key(self):
        """Test getting a missing key returns None."""
        data = {"name": "Alice"}
        assert get(data, "age") is None
        assert get(data, "user.name") is None
    
    def test_get_from_none(self):
        """Test getting from None returns None."""
        assert get(None, "any.path") is None


class TestListAccess:
    """Test accessing list elements."""
    
    def test_get_list_index(self):
        """Test getting list elements by index."""
        data = {"items": ["a", "b", "c"]}
        assert get(data, "items.0") == "a"
        assert get(data, "items.1") == "b"
        assert get(data, "items.2") == "c"
    
    def test_get_negative_index(self):
        """Test negative list indices."""
        data = {"items": ["a", "b", "c"]}
        assert get(data, "items.-1") == "c"
        assert get(data, "items.-2") == "b"
    
    def test_get_out_of_bounds(self):
        """Test out of bounds list access returns None."""
        data = {"items": ["a", "b"]}
        assert get(data, "items.5") is None
        assert get(data, "items.-10") is None
    
    def test_get_nested_list(self):
        """Test accessing nested lists."""
        data = {"matrix": [[1, 2], [3, 4]]}
        assert get(data, "matrix.0.0") == 1
        assert get(data, "matrix.0.1") == 2
        assert get(data, "matrix.1.0") == 3
        assert get(data, "matrix.1.1") == 4
    
    def test_get_dict_in_list(self):
        """Test accessing dictionaries within lists."""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        assert get(data, "users.0.name") == "Alice"
        assert get(data, "users.1.name") == "Bob"


class TestMixedStructures:
    """Test mixed dict/list structures."""
    
    def test_complex_nesting(self):
        """Test complex nested structures."""
        data = {
            "company": {
                "departments": [
                    {
                        "name": "Engineering",
                        "teams": [
                            {"name": "Backend", "size": 5},
                            {"name": "Frontend", "size": 3}
                        ]
                    },
                    {
                        "name": "Sales",
                        "teams": [
                            {"name": "Enterprise", "size": 10}
                        ]
                    }
                ]
            }
        }
        
        assert get(data, "company.departments.0.name") == "Engineering"
        assert get(data, "company.departments.0.teams.0.name") == "Backend"
        assert get(data, "company.departments.0.teams.0.size") == 5
        assert get(data, "company.departments.1.teams.0.name") == "Enterprise"
    
    def test_numeric_string_keys(self):
        """Test handling of numeric string keys in dicts."""
        data = {"0": "zero", "1": "one", "items": ["a", "b"]}
        assert get(data, "0") == "zero"
        assert get(data, "1") == "one"
        assert get(data, "items.0") == "a"


class TestEdgeCases:
    """Test edge cases and special values."""
    
    def test_get_empty_path(self):
        """Test empty path returns None."""
        data = {"name": "Alice"}
        assert get(data, "") is None
    
    def test_get_none_values(self):
        """Test getting None values."""
        data = {"value": None}
        assert get(data, "value") is None
    
    def test_get_boolean_values(self):
        """Test getting boolean values."""
        data = {"active": True, "disabled": False}
        assert get(data, "active") is True
        assert get(data, "disabled") is False
    
    def test_get_zero_values(self):
        """Test getting zero values."""
        data = {"count": 0, "price": 0.0}
        assert get(data, "count") == 0
        assert get(data, "price") == 0.0
    
    def test_get_empty_collections(self):
        """Test getting empty collections."""
        data = {"empty_list": [], "empty_dict": {}}
        assert get(data, "empty_list") == []
        assert get(data, "empty_dict") == {}
    
    def test_special_characters_in_keys(self):
        """Test keys with special characters."""
        data = {"user.name": "dotted", "user": {"name": "nested"}}
        # Should handle the nested path, not the literal key
        assert get(data, "user.name") == "nested"
    
    def test_type_errors(self):
        """Test accessing paths through non-dict/list types."""
        data = {"value": 42}
        assert get(data, "value.nested") is None
        
        data = {"text": "hello"}
        assert get(data, "text.0") is None


class TestRealWorldScenarios:
    """Test real-world usage patterns."""
    
    def test_api_response_parsing(self):
        """Test parsing typical API responses."""
        response = {
            "status": "success",
            "data": {
                "user": {
                    "id": 123,
                    "profile": {
                        "firstName": "Alice",
                        "lastName": "Smith",
                        "preferences": {
                            "notifications": {
                                "email": True,
                                "sms": False
                            }
                        }
                    }
                },
                "metadata": {
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            }
        }
        
        assert get(response, "status") == "success"
        assert get(response, "data.user.id") == 123
        assert get(response, "data.user.profile.firstName") == "Alice"
        assert get(response, "data.user.profile.preferences.notifications.email") is True
        assert get(response, "data.metadata.timestamp") == "2024-01-01T00:00:00Z"
    
    def test_configuration_access(self):
        """Test accessing configuration values."""
        config = {
            "database": {
                "connections": {
                    "primary": {
                        "host": "localhost",
                        "port": 5432,
                        "credentials": {
                            "username": "admin",
                            "password": "secret"
                        }
                    }
                }
            },
            "features": {
                "flags": ["feature-a", "feature-b", "feature-c"]
            }
        }
        
        assert get(config, "database.connections.primary.host") == "localhost"
        assert get(config, "database.connections.primary.port") == 5432
        assert get(config, "database.connections.primary.credentials.username") == "admin"
        assert get(config, "features.flags.0") == "feature-a"
        assert get(config, "features.flags.-1") == "feature-c"
    
    def test_safe_navigation(self):
        """Test safe navigation through potentially missing paths."""
        data = {"user": {"name": "Alice"}}
        
        # These should all safely return None
        assert get(data, "user.email") is None
        assert get(data, "user.address.street") is None
        assert get(data, "company.name") is None
        assert get(data, "users.0.name") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])