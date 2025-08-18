"""
Tests for dotexists - Truth pillar primitive for checking path existence.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from truth.dotexists.core import check


class TestBasicExists:
    """Test basic existence checking."""
    
    def test_exists_simple_key(self):
        """Test checking simple top-level keys."""
        data = {"name": "Alice", "age": 30}
        assert check(data, "name") is True
        assert check(data, "age") is True
        assert check(data, "email") is False
    
    def test_exists_nested_key(self):
        """Test checking nested keys."""
        data = {"user": {"name": "Alice", "age": 30}}
        assert check(data, "user") is True
        assert check(data, "user.name") is True
        assert check(data, "user.age") is True
        assert check(data, "user.email") is False
    
    def test_exists_deeply_nested(self):
        """Test checking deeply nested paths."""
        data = {
            "company": {
                "department": {
                    "team": {
                        "lead": "Alice"
                    }
                }
            }
        }
        assert check(data, "company") is True
        assert check(data, "company.department") is True
        assert check(data, "company.department.team") is True
        assert check(data, "company.department.team.lead") is True
        assert check(data, "company.department.team.members") is False
    
    def test_exists_with_none_value(self):
        """Test that None values still count as existing."""
        data = {"value": None, "nested": {"value": None}}
        assert check(data, "value") is True
        assert check(data, "nested.value") is True
    
    def test_exists_with_false_value(self):
        """Test that False values still count as existing."""
        data = {"active": False, "settings": {"enabled": False}}
        assert check(data, "active") is True
        assert check(data, "settings.enabled") is True
    
    def test_exists_with_zero_value(self):
        """Test that zero values still count as existing."""
        data = {"count": 0, "price": 0.0}
        assert check(data, "count") is True
        assert check(data, "price") is True
    
    def test_exists_with_empty_collections(self):
        """Test that empty collections still count as existing."""
        data = {"items": [], "options": {}}
        assert check(data, "items") is True
        assert check(data, "options") is True


class TestListExists:
    """Test existence checking in lists."""
    
    def test_exists_list_index(self):
        """Test checking list elements by index."""
        data = {"items": ["a", "b", "c"]}
        assert check(data, "items.0") is True
        assert check(data, "items.1") is True
        assert check(data, "items.2") is True
        assert check(data, "items.3") is False
    
    def test_exists_negative_index(self):
        """Test checking with negative indices."""
        data = {"items": ["a", "b", "c"]}
        assert check(data, "items.-1") is True
        assert check(data, "items.-2") is True
        assert check(data, "items.-3") is True
        assert check(data, "items.-4") is False
    
    def test_exists_nested_list(self):
        """Test checking existence in nested lists."""
        data = {"matrix": [[1, 2], [3, 4]]}
        assert check(data, "matrix.0") is True
        assert check(data, "matrix.0.0") is True
        assert check(data, "matrix.0.1") is True
        assert check(data, "matrix.0.2") is False
        assert check(data, "matrix.2") is False
    
    def test_exists_dict_in_list(self):
        """Test checking existence in dicts within lists."""
        data = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob"}]}
        assert check(data, "users.0.name") is True
        assert check(data, "users.0.age") is True
        assert check(data, "users.1.name") is True
        assert check(data, "users.1.age") is False


class TestEdgeCases:
    """Test edge cases."""
    
    def test_exists_empty_path(self):
        """Test empty path."""
        data = {"name": "Alice"}
        # Empty path should return False
        assert check(data, "") is False
    
    def test_exists_on_none(self):
        """Test checking existence on None data."""
        assert check(None, "any.path") is False
    
    def test_exists_on_primitives(self):
        """Test checking paths through primitive types."""
        assert check("string", "any.path") is False
        assert check(42, "any.path") is False
        assert check(True, "any.path") is False
    
    def test_numeric_string_keys(self):
        """Test numeric strings as dict keys."""
        data = {"0": "zero", "1": "one", "items": ["a", "b"]}
        assert check(data, "0") is True
        assert check(data, "1") is True
        assert check(data, "2") is False
        assert check(data, "items.0") is True
    
    def test_special_characters_in_keys(self):
        """Test keys with dots and special characters."""
        data = {"user.name": "dotted key", "user": {"name": "nested"}}
        # Should check the nested path, not the literal key
        assert check(data, "user.name") is True
        assert check(data, "user") is True


class TestComplexStructures:
    """Test complex nested structures."""
    
    def test_mixed_nesting(self):
        """Test existence in mixed dict/list structures."""
        data = {
            "company": {
                "departments": [
                    {
                        "name": "Engineering",
                        "teams": [
                            {"name": "Backend", "members": ["Alice", "Bob"]},
                            {"name": "Frontend", "members": ["Charlie"]}
                        ]
                    },
                    {
                        "name": "Sales",
                        "teams": []
                    }
                ]
            }
        }
        
        assert check(data, "company") is True
        assert check(data, "company.departments") is True
        assert check(data, "company.departments.0") is True
        assert check(data, "company.departments.0.name") is True
        assert check(data, "company.departments.0.teams") is True
        assert check(data, "company.departments.0.teams.0") is True
        assert check(data, "company.departments.0.teams.0.members") is True
        assert check(data, "company.departments.0.teams.0.members.0") is True
        assert check(data, "company.departments.0.teams.0.members.5") is False
        assert check(data, "company.departments.1.teams") is True
        assert check(data, "company.departments.1.teams.0") is False
        assert check(data, "company.departments.2") is False
    
    def test_api_response_structure(self):
        """Test typical API response structure."""
        response = {
            "status": "success",
            "data": {
                "user": {
                    "id": 123,
                    "profile": {
                        "firstName": "Alice",
                        "lastName": None,
                        "avatar": None
                    }
                }
            },
            "errors": []
        }
        
        assert check(response, "status") is True
        assert check(response, "data") is True
        assert check(response, "data.user") is True
        assert check(response, "data.user.id") is True
        assert check(response, "data.user.profile") is True
        assert check(response, "data.user.profile.firstName") is True
        assert check(response, "data.user.profile.lastName") is True  # None still exists
        assert check(response, "data.user.profile.avatar") is True  # None still exists
        assert check(response, "data.user.profile.email") is False
        assert check(response, "errors") is True
        assert check(response, "errors.0") is False  # Empty list


class TestUseCases:
    """Test real-world use cases."""
    
    def test_optional_configuration(self):
        """Test checking for optional configuration."""
        config = {
            "database": {
                "host": "localhost",
                "port": 5432
                # username and password might be optional
            }
        }
        
        # Required fields
        assert check(config, "database.host") is True
        assert check(config, "database.port") is True
        
        # Optional fields
        assert check(config, "database.username") is False
        assert check(config, "database.password") is False
        
        # Check before access pattern
        if check(config, "database.ssl"):
            # Would access database.ssl here
            pass
    
    def test_feature_flags(self):
        """Test checking for feature flags."""
        settings = {
            "features": {
                "newUI": True,
                "betaFeature": False,
                "experimentalAPI": None  # Explicitly disabled
            }
        }
        
        assert check(settings, "features.newUI") is True
        assert check(settings, "features.betaFeature") is True
        assert check(settings, "features.experimentalAPI") is True
        assert check(settings, "features.deprecatedFeature") is False
    
    def test_validation_before_access(self):
        """Test validation pattern before accessing nested data."""
        user_data = {
            "user": {
                "name": "Alice",
                "contacts": {
                    "email": "alice@example.com"
                    # phone might not exist
                }
            }
        }
        
        # Safe navigation pattern
        if check(user_data, "user.contacts.phone"):
            # Safe to access user.contacts.phone
            pass
        
        # Check multiple paths
        has_full_contact = (
            check(user_data, "user.contacts.email") and
            check(user_data, "user.contacts.phone")
        )
        assert has_full_contact is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])