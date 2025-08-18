"""
Tests for dotany - Truth pillar's existential quantifier.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from truth.dotany.core import any_match


class TestBasicAnyMatch:
    """Test basic any_match functionality."""
    
    def test_any_match_simple_list(self):
        """Test any_match on simple lists."""
        data = [
            {"status": "active"},
            {"status": "pending"},
            {"status": "inactive"}
        ]
        
        # At least one active
        assert any_match(data, "status", "active") is True
        
        # No completed status
        assert any_match(data, "status", "completed") is False
    
    def test_any_match_nested_objects(self):
        """Test any_match on nested objects."""
        data = [
            {"user": {"role": "admin", "active": True}},
            {"user": {"role": "user", "active": False}},
            {"user": {"role": "user", "active": True}}
        ]
        
        # At least one admin
        assert any_match(data, "user.role", "admin") is True
        
        # At least one active user
        assert any_match(data, "user.active", True) is True
        
        # No moderators
        assert any_match(data, "user.role", "moderator") is False
    
    def test_any_match_empty_collection(self):
        """Test any_match on empty collections."""
        data = []
        
        # Empty collection never has any matches
        assert any_match(data, "any.path", "any_value") is False
    
    def test_any_match_missing_paths(self):
        """Test any_match with missing paths."""
        data = [
            {"name": "Alice"},
            {"name": "Bob", "age": 30}
        ]
        
        # At least one has age=30
        assert any_match(data, "age", 30) is True
        
        # None have email field
        assert any_match(data, "email", "test@example.com") is False
    
    def test_any_match_with_none_values(self):
        """Test any_match with None values."""
        data = [
            {"value": None},
            {"value": 42},
            {"value": None}
        ]
        
        # At least one None
        assert any_match(data, "value", None) is True
        
        # At least one 42
        assert any_match(data, "value", 42) is True
        
        # No 0 values
        assert any_match(data, "value", 0) is False


class TestComplexDataStructures:
    """Test with complex nested structures."""
    
    def test_deeply_nested_paths(self):
        """Test any_match with deeply nested paths."""
        data = [
            {
                "company": {
                    "department": {
                        "team": {
                            "lead": "Alice"
                        }
                    }
                }
            },
            {
                "company": {
                    "department": {
                        "team": {
                            "lead": "Bob"
                        }
                    }
                }
            }
        ]
        
        assert any_match(data, "company.department.team.lead", "Alice") is True
        assert any_match(data, "company.department.team.lead", "Charlie") is False
    
    def test_list_within_objects(self):
        """Test any_match when objects contain lists."""
        data = [
            {"tags": ["python", "data"]},
            {"tags": ["java", "web"]},
            {"tags": ["python", "ml"]}
        ]
        
        # This tests if the entire tags array equals the value
        # Not if tags contains the value
        assert any_match(data, "tags", ["python", "data"]) is True
        assert any_match(data, "tags", ["python"]) is False
    
    def test_mixed_types(self):
        """Test any_match with mixed data types."""
        data = [
            {"id": 1},
            {"id": "2"},
            {"id": 3.0},
            {"id": True}
        ]
        
        assert any_match(data, "id", 1) is True
        assert any_match(data, "id", "2") is True
        assert any_match(data, "id", 3.0) is True
        assert any_match(data, "id", True) is True
        assert any_match(data, "id", False) is False


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_single_item_collection(self):
        """Test any_match with single item."""
        data = [{"value": 42}]
        
        assert any_match(data, "value", 42) is True
        assert any_match(data, "value", 0) is False
    
    def test_boolean_values(self):
        """Test any_match with boolean values."""
        data = [
            {"active": True},
            {"active": False},
            {"active": True}
        ]
        
        assert any_match(data, "active", True) is True
        assert any_match(data, "active", False) is True
    
    def test_zero_and_empty_values(self):
        """Test any_match with zero and empty values."""
        data = [
            {"count": 0},
            {"count": 5},
            {"text": ""},
            {"text": "hello"}
        ]
        
        assert any_match(data, "count", 0) is True
        assert any_match(data, "text", "") is True
    
    def test_case_sensitivity(self):
        """Test that matching is case-sensitive."""
        data = [
            {"name": "Alice"},
            {"name": "alice"},
            {"name": "ALICE"}
        ]
        
        assert any_match(data, "name", "Alice") is True
        assert any_match(data, "name", "alice") is True
        assert any_match(data, "name", "ALICE") is True
        assert any_match(data, "name", "aLiCe") is False


class TestRealWorldScenarios:
    """Test real-world usage patterns."""
    
    def test_user_permissions(self):
        """Test checking user permissions."""
        users = [
            {"username": "alice", "role": "admin", "active": True},
            {"username": "bob", "role": "user", "active": True},
            {"username": "charlie", "role": "user", "active": False}
        ]
        
        # Check if any admin exists
        assert any_match(users, "role", "admin") is True
        
        # Check if any inactive user exists
        assert any_match(users, "active", False) is True
        
        # Check if specific user exists
        assert any_match(users, "username", "alice") is True
        assert any_match(users, "username", "david") is False
    
    def test_product_inventory(self):
        """Test checking product inventory."""
        products = [
            {"name": "Laptop", "inStock": True, "price": 999},
            {"name": "Mouse", "inStock": False, "price": 25},
            {"name": "Keyboard", "inStock": True, "price": 75}
        ]
        
        # Check if any product is out of stock
        assert any_match(products, "inStock", False) is True
        
        # Check if any expensive product exists (exact price match)
        assert any_match(products, "price", 999) is True
        assert any_match(products, "price", 1000) is False
    
    def test_log_entries(self):
        """Test checking log entries."""
        logs = [
            {"level": "INFO", "service": "api", "message": "Request received"},
            {"level": "ERROR", "service": "db", "message": "Connection failed"},
            {"level": "INFO", "service": "api", "message": "Request completed"}
        ]
        
        # Check if any errors exist
        assert any_match(logs, "level", "ERROR") is True
        
        # Check if any db service logs exist
        assert any_match(logs, "service", "db") is True
        
        # Check if any critical errors exist
        assert any_match(logs, "level", "CRITICAL") is False
    
    def test_configuration_validation(self):
        """Test validating configurations."""
        configs = [
            {"env": "development", "debug": True, "port": 3000},
            {"env": "staging", "debug": False, "port": 3001},
            {"env": "production", "debug": False, "port": 80}
        ]
        
        # Check if any config has debug enabled
        assert any_match(configs, "debug", True) is True
        
        # Check if any production environment exists
        assert any_match(configs, "env", "production") is True
        
        # Check if any config uses default port 80
        assert any_match(configs, "port", 80) is True


class TestArrayAccess:
    """Test accessing array elements within documents."""
    
    def test_array_element_matching(self):
        """Test matching specific array elements."""
        data = [
            {"values": [1, 2, 3]},
            {"values": [4, 5, 6]},
            {"values": [7, 8, 9]}
        ]
        
        # Check first element of values array
        assert any_match(data, "values.0", 1) is True
        assert any_match(data, "values.0", 4) is True
        assert any_match(data, "values.0", 7) is True
        assert any_match(data, "values.0", 2) is False
    
    def test_nested_array_access(self):
        """Test accessing nested arrays."""
        data = [
            {"matrix": [[1, 2], [3, 4]]},
            {"matrix": [[5, 6], [7, 8]]}
        ]
        
        # Check specific positions in matrix
        assert any_match(data, "matrix.0.0", 1) is True
        assert any_match(data, "matrix.0.0", 5) is True
        assert any_match(data, "matrix.1.1", 4) is True
        assert any_match(data, "matrix.1.1", 8) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])