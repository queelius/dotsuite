"""
Tests for dotall - Truth pillar's universal quantifier.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from truth.dotall.core import all_match


class TestBasicAllMatch:
    """Test basic all_match functionality."""
    
    def test_all_match_simple_list(self):
        """Test all_match on simple lists."""
        data = [
            {"status": "active"},
            {"status": "active"},
            {"status": "active"}
        ]
        
        # All are active
        assert all_match(data, "status", "active") is True
        
        # Add one inactive
        data.append({"status": "inactive"})
        assert all_match(data, "status", "active") is False
    
    def test_all_match_nested_objects(self):
        """Test all_match on nested objects."""
        data = [
            {"user": {"role": "admin", "active": True}},
            {"user": {"role": "admin", "active": True}},
            {"user": {"role": "admin", "active": True}}
        ]
        
        # All are admin
        assert all_match(data, "user.role", "admin") is True
        
        # All are active
        assert all_match(data, "user.active", True) is True
        
        # Change one to user role
        data[1]["user"]["role"] = "user"
        assert all_match(data, "user.role", "admin") is False
    
    def test_all_match_empty_collection(self):
        """Test all_match on empty collections."""
        data = []
        
        # Empty collection - vacuous truth (all zero elements satisfy any predicate)
        assert all_match(data, "any.path", "any_value") is True
    
    def test_all_match_missing_paths(self):
        """Test all_match with missing paths."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 30},
            {"name": "Charlie"}  # Missing age
        ]
        
        # Not all have age=30 (one missing)
        assert all_match(data, "age", 30) is False
        
        # All have name field
        data = [
            {"name": "Alice"},
            {"name": "Bob"},
            {"name": "Charlie"}
        ]
        # Even though all have names, we're checking specific value
        assert all_match(data, "name", "Alice") is False
    
    def test_all_match_with_none_values(self):
        """Test all_match with None values."""
        data = [
            {"value": None},
            {"value": None},
            {"value": None}
        ]
        
        # All are None
        assert all_match(data, "value", None) is True
        
        # Change one to non-None
        data[1]["value"] = 42
        assert all_match(data, "value", None) is False


class TestComplexDataStructures:
    """Test with complex nested structures."""
    
    def test_deeply_nested_paths(self):
        """Test all_match with deeply nested paths."""
        data = [
            {
                "company": {
                    "department": {
                        "team": {
                            "status": "active"
                        }
                    }
                }
            },
            {
                "company": {
                    "department": {
                        "team": {
                            "status": "active"
                        }
                    }
                }
            }
        ]
        
        assert all_match(data, "company.department.team.status", "active") is True
        
        # Change one
        data[0]["company"]["department"]["team"]["status"] = "inactive"
        assert all_match(data, "company.department.team.status", "active") is False
    
    def test_uniform_collections(self):
        """Test all_match when all documents are identical."""
        data = [
            {"id": 1, "type": "user", "verified": True},
            {"id": 2, "type": "user", "verified": True},
            {"id": 3, "type": "user", "verified": True}
        ]
        
        assert all_match(data, "type", "user") is True
        assert all_match(data, "verified", True) is True
        assert all_match(data, "type", "admin") is False
    
    def test_mixed_types(self):
        """Test all_match with mixed data types."""
        # All have same value but different types won't match
        data = [
            {"id": "1"},
            {"id": "1"},
            {"id": "1"}
        ]
        
        assert all_match(data, "id", "1") is True
        assert all_match(data, "id", 1) is False  # Type mismatch


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_single_item_collection(self):
        """Test all_match with single item."""
        data = [{"value": 42}]
        
        assert all_match(data, "value", 42) is True
        assert all_match(data, "value", 0) is False
    
    def test_boolean_values(self):
        """Test all_match with boolean values."""
        data = [
            {"active": True},
            {"active": True},
            {"active": True}
        ]
        
        assert all_match(data, "active", True) is True
        assert all_match(data, "active", False) is False
        
        # Mix in a False
        data[1]["active"] = False
        assert all_match(data, "active", True) is False
    
    def test_zero_and_empty_values(self):
        """Test all_match with zero and empty values."""
        data = [
            {"count": 0},
            {"count": 0},
            {"count": 0}
        ]
        
        assert all_match(data, "count", 0) is True
        
        data = [
            {"text": ""},
            {"text": ""},
            {"text": ""}
        ]
        
        assert all_match(data, "text", "") is True
    
    def test_case_sensitivity(self):
        """Test that matching is case-sensitive."""
        data = [
            {"name": "ACTIVE"},
            {"name": "ACTIVE"},
            {"name": "ACTIVE"}
        ]
        
        assert all_match(data, "name", "ACTIVE") is True
        assert all_match(data, "name", "active") is False
        assert all_match(data, "name", "Active") is False


class TestRealWorldScenarios:
    """Test real-world usage patterns."""
    
    def test_user_verification(self):
        """Test checking if all users are verified."""
        users = [
            {"username": "alice", "verified": True, "active": True},
            {"username": "bob", "verified": True, "active": True},
            {"username": "charlie", "verified": True, "active": False}
        ]
        
        # All users are verified
        assert all_match(users, "verified", True) is True
        
        # Not all users are active
        assert all_match(users, "active", True) is False
        
        # Add unverified user
        users.append({"username": "david", "verified": False, "active": True})
        assert all_match(users, "verified", True) is False
    
    def test_product_availability(self):
        """Test checking product availability."""
        products = [
            {"name": "Laptop", "inStock": True, "category": "electronics"},
            {"name": "Mouse", "inStock": True, "category": "electronics"},
            {"name": "Keyboard", "inStock": True, "category": "electronics"}
        ]
        
        # All products in stock
        assert all_match(products, "inStock", True) is True
        
        # All products are electronics
        assert all_match(products, "category", "electronics") is True
        
        # Mark one out of stock
        products[1]["inStock"] = False
        assert all_match(products, "inStock", True) is False
    
    def test_configuration_consistency(self):
        """Test configuration consistency across environments."""
        configs = [
            {"env": "server1", "version": "2.0.0", "ssl": True},
            {"env": "server2", "version": "2.0.0", "ssl": True},
            {"env": "server3", "version": "2.0.0", "ssl": True}
        ]
        
        # All servers on same version
        assert all_match(configs, "version", "2.0.0") is True
        
        # All have SSL enabled
        assert all_match(configs, "ssl", True) is True
        
        # Update one server
        configs[0]["version"] = "2.0.1"
        assert all_match(configs, "version", "2.0.0") is False
    
    def test_data_validation(self):
        """Test validating data consistency."""
        records = [
            {"type": "measurement", "unit": "celsius", "valid": True},
            {"type": "measurement", "unit": "celsius", "valid": True},
            {"type": "measurement", "unit": "celsius", "valid": True}
        ]
        
        # All records are measurements
        assert all_match(records, "type", "measurement") is True
        
        # All use same unit
        assert all_match(records, "unit", "celsius") is True
        
        # All are valid
        assert all_match(records, "valid", True) is True
        
        # Invalidate one record
        records[1]["valid"] = False
        assert all_match(records, "valid", True) is False


class TestArrayElements:
    """Test with array elements in documents."""
    
    def test_array_element_consistency(self):
        """Test checking consistency of array elements."""
        data = [
            {"values": [1, 2, 3]},
            {"values": [1, 2, 3]},
            {"values": [1, 2, 3]}
        ]
        
        # All have same first element
        assert all_match(data, "values.0", 1) is True
        
        # Change one
        data[1]["values"][0] = 10
        assert all_match(data, "values.0", 1) is False
    
    def test_missing_array_elements(self):
        """Test when some documents have shorter arrays."""
        data = [
            {"items": ["a", "b", "c"]},
            {"items": ["a", "b"]},  # Missing third element
            {"items": ["a", "b", "c"]}
        ]
        
        # All have "a" as first element
        assert all_match(data, "items.0", "a") is True
        
        # Not all have "c" as third element (one missing)
        assert all_match(data, "items.2", "c") is False


class TestVacuousTruth:
    """Test the vacuous truth behavior for empty collections."""
    
    def test_empty_collection_always_true(self):
        """Test that empty collections always return True."""
        empty = []
        
        # All of nothing is everything
        assert all_match(empty, "any.path", "any_value") is True
        assert all_match(empty, "deeply.nested.path", 42) is True
        assert all_match(empty, "x", None) is True
        assert all_match(empty, "", "") is True
    
    def test_philosophical_edge_cases(self):
        """Test philosophical edge cases of universal quantification."""
        # If we have no users, are all users admins? Yes (vacuously)
        no_users = []
        assert all_match(no_users, "role", "admin") is True
        
        # If we have users but none have a role field, are all roles admin? No
        users_without_roles = [{"name": "Alice"}, {"name": "Bob"}]
        assert all_match(users_without_roles, "role", "admin") is False
        
        # If all users have role=None, do all have role=None? Yes
        users_with_none = [{"role": None}, {"role": None}]
        assert all_match(users_with_none, "role", None) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])