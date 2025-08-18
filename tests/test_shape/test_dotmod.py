"""
Tests for dotmod - Shape pillar's surgical modification tool.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from shape.dotmod.core import set_, delete_, update_, append_


class TestSet:
    """Test the set_ function for immutable value setting."""
    
    def test_set_simple_value(self):
        """Test setting a simple top-level value."""
        data = {"name": "Alice", "age": 30}
        
        result = set_(data, "age", 31)
        assert result == {"name": "Alice", "age": 31}
        # Original unchanged (immutable)
        assert data == {"name": "Alice", "age": 30}
    
    def test_set_nested_value(self):
        """Test setting nested values."""
        data = {"user": {"name": "Alice", "age": 30}}
        
        result = set_(data, "user.age", 31)
        assert result == {"user": {"name": "Alice", "age": 31}}
        assert data["user"]["age"] == 30  # Original unchanged
    
    def test_set_create_path(self):
        """Test that set_ creates missing paths."""
        data = {"user": {"name": "Alice"}}
        
        # Create nested path that doesn't exist
        result = set_(data, "user.address.city", "New York")
        assert result == {
            "user": {
                "name": "Alice",
                "address": {"city": "New York"}
            }
        }
    
    def test_set_create_deep_path(self):
        """Test creating deeply nested paths."""
        data = {}
        
        result = set_(data, "a.b.c.d.e", "deep")
        assert result == {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        assert data == {}  # Original unchanged
    
    def test_set_list_element(self):
        """Test setting list elements."""
        data = {"items": [1, 2, 3]}
        
        result = set_(data, "items.1", 20)
        assert result == {"items": [1, 20, 3]}
        assert data["items"][1] == 2  # Original unchanged
    
    def test_set_extend_list(self):
        """Test that set_ extends lists with None for out-of-bounds indices."""
        data = {"items": [1, 2]}
        
        result = set_(data, "items.5", 10)
        assert result == {"items": [1, 2, None, None, None, 10]}
    
    def test_set_nested_list(self):
        """Test setting values in nested lists."""
        data = {"matrix": [[1, 2], [3, 4]]}
        
        result = set_(data, "matrix.0.1", 20)
        assert result == {"matrix": [[1, 20], [3, 4]]}
    
    def test_set_none_value(self):
        """Test setting None values."""
        data = {"value": 42}
        
        result = set_(data, "value", None)
        assert result == {"value": None}
    
    def test_set_create_list_path(self):
        """Test creating paths that include lists."""
        data = {}
        
        # When next segment is digit, create list
        result = set_(data, "items.0", "first")
        assert result == {"items": ["first"]}


class TestDelete:
    """Test the delete_ function for immutable deletion."""
    
    def test_delete_simple_key(self):
        """Test deleting a simple top-level key."""
        data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
        
        result = delete_(data, "email")
        assert result == {"name": "Alice", "age": 30}
        assert "email" in data  # Original unchanged
    
    def test_delete_nested_key(self):
        """Test deleting nested keys."""
        data = {"user": {"name": "Alice", "age": 30, "email": "alice@example.com"}}
        
        result = delete_(data, "user.email")
        assert result == {"user": {"name": "Alice", "age": 30}}
        assert "email" in data["user"]  # Original unchanged
    
    def test_delete_list_element(self):
        """Test deleting list elements."""
        data = {"items": [1, 2, 3, 4, 5]}
        
        result = delete_(data, "items.2")
        assert result == {"items": [1, 2, 4, 5]}
        assert len(data["items"]) == 5  # Original unchanged
    
    def test_delete_missing_path(self):
        """Test deleting non-existent paths returns unchanged copy."""
        data = {"name": "Alice"}
        
        result = delete_(data, "missing.path")
        assert result == {"name": "Alice"}
        assert result is not data  # Still a copy
    
    def test_delete_from_nested_structure(self):
        """Test deleting from complex nested structures."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ]
        }
        
        result = delete_(data, "users.0.age")
        assert result == {
            "users": [
                {"name": "Alice"},
                {"name": "Bob", "age": 25}
            ]
        }
    
    def test_delete_entire_branch(self):
        """Test deleting entire nested branches."""
        data = {"a": {"b": {"c": 1, "d": 2}, "e": 3}}
        
        result = delete_(data, "a.b")
        assert result == {"a": {"e": 3}}


class TestUpdate:
    """Test the update_ function for merging dictionaries."""
    
    def test_update_simple_dict(self):
        """Test updating a simple dictionary."""
        data = {"user": {"name": "Alice", "age": 30}}
        
        result = update_(data, "user", {"email": "alice@example.com", "age": 31})
        assert result == {
            "user": {
                "name": "Alice",
                "age": 31,  # Updated
                "email": "alice@example.com"  # Added
            }
        }
        assert "email" not in data["user"]  # Original unchanged
    
    def test_update_nested_dict(self):
        """Test updating nested dictionaries."""
        data = {"config": {"server": {"host": "localhost", "port": 8080}}}
        
        result = update_(data, "config.server", {"port": 9090, "ssl": True})
        assert result == {
            "config": {
                "server": {
                    "host": "localhost",
                    "port": 9090,
                    "ssl": True
                }
            }
        }
    
    def test_update_empty_dict(self):
        """Test updating an empty dictionary."""
        data = {"settings": {}}
        
        result = update_(data, "settings", {"theme": "dark", "lang": "en"})
        assert result == {"settings": {"theme": "dark", "lang": "en"}}
    
    def test_update_non_dict_raises(self):
        """Test that update_ raises TypeError for non-dict values."""
        data = {"value": 42}
        
        with pytest.raises(TypeError, match="must be a dictionary"):
            update_(data, "value", ["not", "a", "dict"])
    
    def test_update_to_non_dict_no_change(self):
        """Test updating a non-dict target does nothing."""
        data = {"value": 42}
        
        result = update_(data, "value", {"key": "value"})
        assert result == {"value": 42}  # No change when target isn't dict
    
    def test_update_missing_path(self):
        """Test updating a non-existent path."""
        data = {"a": 1}
        
        result = update_(data, "missing.path", {"key": "value"})
        assert result == {"a": 1}  # No change when path doesn't exist


class TestAppend:
    """Test the append_ function for list operations."""
    
    def test_append_to_list(self):
        """Test appending to a simple list."""
        data = {"items": [1, 2, 3]}
        
        result = append_(data, "items", 4)
        assert result == {"items": [1, 2, 3, 4]}
        assert len(data["items"]) == 3  # Original unchanged
    
    def test_append_to_nested_list(self):
        """Test appending to nested lists."""
        data = {"user": {"tags": ["python", "data"]}}
        
        result = append_(data, "user.tags", "ml")
        assert result == {"user": {"tags": ["python", "data", "ml"]}}
    
    def test_append_to_empty_list(self):
        """Test appending to an empty list."""
        data = {"items": []}
        
        result = append_(data, "items", "first")
        assert result == {"items": ["first"]}
    
    def test_append_complex_value(self):
        """Test appending complex values."""
        data = {"users": [{"name": "Alice"}]}
        
        new_user = {"name": "Bob", "age": 25}
        result = append_(data, "users", new_user)
        assert result == {"users": [{"name": "Alice"}, {"name": "Bob", "age": 25}]}
    
    def test_append_to_non_list_no_change(self):
        """Test that appending to non-list does nothing."""
        data = {"value": 42}
        
        result = append_(data, "value", "item")
        assert result == {"value": 42}  # No change when target isn't list
    
    def test_append_to_missing_path(self):
        """Test appending to non-existent path."""
        data = {"a": 1}
        
        result = append_(data, "missing.path", "item")
        assert result == {"a": 1}  # No change when path doesn't exist
    
    def test_append_none_value(self):
        """Test appending None values."""
        data = {"items": [1, 2]}
        
        result = append_(data, "items", None)
        assert result == {"items": [1, 2, None]}


class TestImmutability:
    """Test that all operations are truly immutable."""
    
    def test_deep_immutability(self):
        """Test that nested structures aren't modified."""
        data = {
            "level1": {
                "level2": {
                    "items": [1, 2, 3],
                    "value": 42
                }
            }
        }
        
        # Perform various operations
        result1 = set_(data, "level1.level2.value", 100)
        result2 = delete_(data, "level1.level2.items.1")
        result3 = update_(data, "level1.level2", {"new_key": "new_value"})
        result4 = append_(data, "level1.level2.items", 4)
        
        # Original should be completely unchanged
        assert data == {
            "level1": {
                "level2": {
                    "items": [1, 2, 3],
                    "value": 42
                }
            }
        }
        
        # Each result should be different
        assert result1["level1"]["level2"]["value"] == 100
        assert result2["level1"]["level2"]["items"] == [1, 3]
        assert "new_key" in result3["level1"]["level2"]
        assert result4["level1"]["level2"]["items"] == [1, 2, 3, 4]
    
    def test_multiple_operations_chain(self):
        """Test chaining multiple operations."""
        data = {"user": {"name": "Alice"}}
        
        # Chain operations
        result = set_(data, "user.age", 30)
        result = set_(result, "user.email", "alice@example.com")
        result = update_(result, "user", {"verified": True})
        
        assert result == {
            "user": {
                "name": "Alice",
                "age": 30,
                "email": "alice@example.com",
                "verified": True
            }
        }
        
        # Original still unchanged
        assert data == {"user": {"name": "Alice"}}


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_empty_path(self):
        """Test operations with empty paths."""
        data = {"a": 1}
        
        # Empty path creates/deletes empty string key
        result = set_(data, "", "value")
        assert result == {"a": 1, "": "value"}
        
        result = delete_({"a": 1, "": "value"}, "")
        assert result == {"a": 1}
    
    def test_operations_on_none(self):
        """Test operations on None values."""
        data = {"value": None}
        
        result = set_(data, "value.nested", "test")
        # Can't traverse through None, returns original
        assert result == {"value": None}
    
    def test_numeric_string_keys(self):
        """Test handling numeric strings as dict keys vs list indices."""
        # Dictionary with numeric string key
        data = {"0": "zero", "items": ["a", "b"]}
        
        result = set_(data, "0", "ZERO")
        assert result == {"0": "ZERO", "items": ["a", "b"]}
        
        result = set_(data, "items.0", "A")
        assert result == {"0": "zero", "items": ["A", "b"]}
    
    def test_special_characters_in_keys(self):
        """Test keys with dots (edge case for path splitting)."""
        # This is a limitation - dots in keys can't be addressed
        data = {"user.name": "dotted key", "user": {"name": "nested"}}
        
        # Will access the nested path, not the dotted key
        result = set_(data, "user.name", "Bob")
        assert result == {"user.name": "dotted key", "user": {"name": "Bob"}}


class TestRealWorldScenarios:
    """Test real-world usage patterns."""
    
    def test_user_profile_update(self):
        """Test updating user profile data."""
        user = {
            "id": 123,
            "profile": {
                "name": "Alice",
                "email": "alice@old.com",
                "preferences": {
                    "theme": "light",
                    "notifications": True
                }
            },
            "posts": []
        }
        
        # Update email
        user = set_(user, "profile.email", "alice@new.com")
        
        # Update preferences
        user = update_(user, "profile.preferences", {
            "theme": "dark",
            "language": "en"
        })
        
        # Add a post
        user = append_(user, "posts", {"id": 1, "title": "First Post"})
        
        assert user["profile"]["email"] == "alice@new.com"
        assert user["profile"]["preferences"]["theme"] == "dark"
        assert user["profile"]["preferences"]["language"] == "en"
        assert len(user["posts"]) == 1
    
    def test_configuration_management(self):
        """Test managing configuration settings."""
        config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {
                    "user": "admin",
                    "password": "old_pass"
                }
            },
            "features": ["feature1", "feature2"]
        }
        
        # Update password
        config = set_(config, "database.credentials.password", "new_pass")
        
        # Add SSL configuration
        config = set_(config, "database.ssl.enabled", True)
        config = set_(config, "database.ssl.cert", "/path/to/cert")
        
        # Add new feature
        config = append_(config, "features", "feature3")
        
        # Remove old feature
        config = delete_(config, "features.0")
        
        assert config["database"]["credentials"]["password"] == "new_pass"
        assert config["database"]["ssl"]["enabled"] is True
        assert config["features"] == ["feature2", "feature3"]
    
    def test_nested_data_migration(self):
        """Test migrating/transforming nested data structures."""
        old_format = {
            "user_data": {
                "personal_info": {
                    "full_name": "Alice Smith",
                    "years_old": 30
                }
            }
        }
        
        # Transform to new format
        new_format = set_({}, "user.name", "Alice Smith")
        new_format = set_(new_format, "user.age", 30)
        new_format = set_(new_format, "metadata.migrated", True)
        new_format = set_(new_format, "metadata.version", "2.0")
        
        assert new_format == {
            "user": {
                "name": "Alice Smith",
                "age": 30
            },
            "metadata": {
                "migrated": True,
                "version": "2.0"
            }
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])