"""
Comprehensive tests for dotquery DSL parser.
These tests serve as both validation and specification for the DSL syntax.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from truth.dotquery.core import (
    Query, parse_dsl, Condition, And, Or, Not,
    DSLError, DSLSyntaxError, UnknownOperatorError, MissingValueError
)
import operator


class TestDSLBasicSyntax:
    """Test basic DSL syntax parsing."""
    
    def test_simple_equals(self):
        """Test basic equality checks."""
        # String value
        q = Query("status equals active")
        assert q.evaluate({"status": "active"}) is True
        assert q.evaluate({"status": "inactive"}) is False
        
        # Numeric value
        q = Query("age equals 25")
        assert q.evaluate({"age": 25}) is True
        assert q.evaluate({"age": 30}) is False
        
        # Boolean value
        q = Query("enabled equals true")
        assert q.evaluate({"enabled": True}) is True
        assert q.evaluate({"enabled": False}) is False
        
        q = Query("disabled equals false")
        assert q.evaluate({"disabled": False}) is True
        assert q.evaluate({"disabled": True}) is False
        
        # Null value
        q = Query("deleted equals null")
        assert q.evaluate({"deleted": None}) is True
        assert q.evaluate({"deleted": "something"}) is False
    
    def test_alternative_equals_syntax(self):
        """Test alternative syntax for equality."""
        data = {"status": "active", "count": 42}
        
        # Different equality operators
        for op in ["equals", "eq", "=", "=="]:
            q = Query(f"status {op} active")
            assert q.evaluate(data) is True
            
            q = Query(f"count {op} 42")
            assert q.evaluate(data) is True
    
    def test_not_equals(self):
        """Test inequality checks."""
        data = {"status": "active", "count": 42}
        
        for op in ["not_equals", "ne", "!="]:
            q = Query(f"status {op} inactive")
            assert q.evaluate(data) is True
            
            q = Query(f"count {op} 0")
            assert q.evaluate(data) is True
    
    def test_comparison_operators(self):
        """Test numeric comparison operators."""
        data = {"age": 25, "score": 85.5}
        
        # Greater than
        for op in ["greater", "gt", ">"]:
            q = Query(f"age {op} 20")
            assert q.evaluate(data) is True
            q = Query(f"age {op} 30")
            assert q.evaluate(data) is False
        
        # Greater or equal
        for op in ["greater_equal", "ge", ">="]:
            q = Query(f"age {op} 25")
            assert q.evaluate(data) is True
            q = Query(f"age {op} 26")
            assert q.evaluate(data) is False
        
        # Less than
        for op in ["less", "lt", "<"]:
            q = Query(f"score {op} 90")
            assert q.evaluate(data) is True
            q = Query(f"score {op} 80")
            assert q.evaluate(data) is False
        
        # Less or equal
        for op in ["less_equal", "le", "<="]:
            q = Query(f"score {op} 85.5")
            assert q.evaluate(data) is True
            q = Query(f"score {op} 85")
            assert q.evaluate(data) is False
    
    def test_contains_operator(self):
        """Test contains operator."""
        data = {"tags": ["python", "data", "ml"], "name": "Alice"}
        
        for op in ["contains", "in"]:
            q = Query(f"tags {op} python")
            assert q.evaluate(data) is True
            
            q = Query(f"tags {op} java")
            assert q.evaluate(data) is False
            
            # String contains (substring)
            q = Query(f"name {op} li")
            assert q.evaluate(data) is True
    
    def test_matches_regex(self):
        """Test regex matching."""
        data = {"email": "alice@example.com", "code": "ABC123"}
        
        for op in ["matches", "regex"]:
            q = Query(f"email {op} .*@example\\.com")
            assert q.evaluate(data) is True
            
            q = Query(f"code {op} [A-Z]+[0-9]+")
            assert q.evaluate(data) is True
            
            q = Query(f"code {op} ^[0-9]+$")
            assert q.evaluate(data) is False
    
    def test_exists_operator(self):
        """Test existence checking."""
        data = {"name": "Alice", "age": 0, "empty": "", "null": None}
        
        q = Query("name exists")
        assert q.evaluate(data) is True
        
        q = Query("age exists")
        assert q.evaluate(data) is False  # 0 is falsy
        
        q = Query("empty exists")
        assert q.evaluate(data) is False  # Empty string is falsy
        
        q = Query("null exists")
        assert q.evaluate(data) is False  # None is falsy
        
        q = Query("missing exists")
        assert q.evaluate(data) is False  # Missing key


class TestDSLQuantifiers:
    """Test quantifier syntax in DSL."""
    
    def test_any_quantifier_explicit(self):
        """Test explicit any quantifier."""
        data = {
            "numbers": [1, 2, 3, 4, 5],
            "users": [
                {"name": "Alice", "admin": True},
                {"name": "Bob", "admin": False}
            ]
        }
        
        # Any number greater than 3
        q = Query("any numbers greater 3")
        assert q.evaluate(data) is True
        
        q = Query("any numbers greater 10")
        assert q.evaluate(data) is False
        
        # Any user is admin
        q = Query("any users.admin equals true")
        assert q.evaluate(data) is True
    
    def test_all_quantifier(self):
        """Test all quantifier."""
        data = {
            "numbers": [1, 2, 3, 4, 5],
            "positives": [1, 2, 3],
            "users": [
                {"name": "Alice", "verified": True},
                {"name": "Bob", "verified": True}
            ]
        }
        
        # All numbers greater than 0
        q = Query("all numbers greater 0")
        assert q.evaluate(data) is True
        
        q = Query("all numbers greater 3")
        assert q.evaluate(data) is False
        
        # All positives less than 10
        q = Query("all positives less 10")
        assert q.evaluate(data) is True
        
        # All users verified
        q = Query("all users.verified equals true")
        assert q.evaluate(data) is True
    
    def test_quantifier_with_empty_collection(self):
        """Test quantifiers on empty collections."""
        data = {"items": [], "users": []}
        
        # Any item - always false for empty
        q = Query("any items greater 0")
        assert q.evaluate(data) is False
        
        # All items - vacuous truth for empty
        q = Query("all items greater 0")
        assert q.evaluate(data) is True
        
        q = Query("all users.admin equals true")
        assert q.evaluate(data) is True  # Vacuous truth


class TestDSLLogicalOperators:
    """Test logical operators in DSL."""
    
    def test_and_operator(self):
        """Test AND operator."""
        data = {"status": "active", "age": 25, "verified": True}
        
        # Both conditions true
        q = Query("(status equals active) and (age greater 20)")
        assert q.evaluate(data) is True
        
        # One condition false
        q = Query("(status equals active) and (age greater 30)")
        assert q.evaluate(data) is False
        
        # Both conditions false
        q = Query("(status equals inactive) and (age less 20)")
        assert q.evaluate(data) is False
        
        # Multiple AND
        q = Query("(status equals active) and (age greater 20) and (verified equals true)")
        assert q.evaluate(data) is True
    
    def test_or_operator(self):
        """Test OR operator."""
        data = {"status": "active", "age": 25, "role": "user"}
        
        # Both conditions true
        q = Query("(status equals active) or (age greater 20)")
        assert q.evaluate(data) is True
        
        # One condition true
        q = Query("(status equals inactive) or (age greater 20)")
        assert q.evaluate(data) is True
        
        # Both conditions false
        q = Query("(status equals inactive) or (age less 20)")
        assert q.evaluate(data) is False
        
        # Multiple OR
        q = Query("(role equals admin) or (role equals moderator) or (role equals user)")
        assert q.evaluate(data) is True
    
    def test_not_operator(self):
        """Test NOT operator."""
        data = {"status": "active", "deleted": False}
        
        q = Query("not status equals inactive")
        assert q.evaluate(data) is True
        
        q = Query("not status equals active")
        assert q.evaluate(data) is False
        
        q = Query("not deleted equals true")
        assert q.evaluate(data) is True
        
        # Double negation
        q = Query("not not status equals active")
        assert q.evaluate(data) is True
    
    def test_complex_logical_expressions(self):
        """Test complex combinations of logical operators."""
        data = {
            "user": {
                "name": "Alice",
                "age": 25,
                "role": "admin",
                "verified": True
            }
        }
        
        # (admin OR moderator) AND verified
        q = Query("((user.role equals admin) or (user.role equals moderator)) and (user.verified equals true)")
        assert q.evaluate(data) is True
        
        # NOT (young AND unverified)
        q = Query("not ((user.age less 18) and (user.verified equals false))")
        assert q.evaluate(data) is True
        
        # Complex nested expression
        q = Query("(user.verified equals true) and ((user.role equals admin) or (user.age greater 21))")
        assert q.evaluate(data) is True


class TestDSLNestedPaths:
    """Test DSL with nested data paths."""
    
    def test_simple_nested_paths(self):
        """Test simple nested path access."""
        data = {
            "user": {
                "profile": {
                    "name": "Alice",
                    "age": 30
                },
                "settings": {
                    "theme": "dark"
                }
            }
        }
        
        q = Query("user.profile.name equals Alice")
        assert q.evaluate(data) is True
        
        q = Query("user.profile.age greater 25")
        assert q.evaluate(data) is True
        
        q = Query("user.settings.theme equals dark")
        assert q.evaluate(data) is True
    
    def test_array_element_paths(self):
        """Test paths with array indices."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "matrix": [[1, 2, 3], [4, 5, 6]]
        }
        
        q = Query("users.0.name equals Alice")
        assert q.evaluate(data) is True
        
        q = Query("users.1.age less 30")
        assert q.evaluate(data) is True
        
        q = Query("matrix.0.2 equals 3")
        assert q.evaluate(data) is True
        
        q = Query("matrix.1.0 greater 3")
        assert q.evaluate(data) is True
    
    def test_wildcard_paths(self):
        """Test implicit wildcard expansion."""
        data = {
            "users": [
                {"name": "Alice", "active": True},
                {"name": "Bob", "active": True},
                {"name": "Charlie", "active": False}
            ]
        }
        
        # Implicit wildcard - should expand to users.*.active
        q = Query("any users.active equals true")
        assert q.evaluate(data) is True
        
        q = Query("all users.active equals true")
        assert q.evaluate(data) is False
        
        # Check if any user name contains 'li'
        q = Query("any users.name contains li")
        assert q.evaluate(data) is True


class TestDSLValueParsing:
    """Test how DSL parses different value types."""
    
    def test_string_values(self):
        """Test string value parsing."""
        data = {"status": "active", "message": "hello world"}
        
        # Simple strings (no quotes needed)
        q = Query("status equals active")
        assert q.evaluate(data) is True
        
        # Strings with spaces need quotes
        q = Query('message equals "hello world"')
        assert q.evaluate(data) is True
        
        q = Query("message equals 'hello world'")
        assert q.evaluate(data) is True
    
    def test_numeric_values(self):
        """Test numeric value parsing."""
        data = {"age": 25, "score": 85.5, "balance": -100.50}
        
        # Integers
        q = Query("age equals 25")
        assert q.evaluate(data) is True
        
        # Floats
        q = Query("score equals 85.5")
        assert q.evaluate(data) is True
        
        # Negative numbers
        q = Query("balance equals -100.50")
        assert q.evaluate(data) is True
        
        q = Query("balance less 0")
        assert q.evaluate(data) is True
    
    def test_boolean_values(self):
        """Test boolean value parsing."""
        data = {"active": True, "deleted": False}
        
        # True values
        q = Query("active equals true")
        assert q.evaluate(data) is True
        
        # False values
        q = Query("deleted equals false")
        assert q.evaluate(data) is True
        
        # Case insensitive
        q = Query("active equals TRUE")
        assert q.evaluate(data) is True
        
        q = Query("deleted equals FALSE")
        assert q.evaluate(data) is True
    
    def test_null_values(self):
        """Test null value parsing."""
        data = {"value": None, "name": "Alice"}
        
        # Null/None values
        q = Query("value equals null")
        assert q.evaluate(data) is True
        
        q = Query("value equals none")
        assert q.evaluate(data) is True
        
        q = Query("name not_equals null")
        assert q.evaluate(data) is True


class TestDSLErrorHandling:
    """Test DSL error handling and edge cases."""
    
    def test_invalid_syntax(self):
        """Test handling of invalid DSL syntax."""
        # Missing operator - should raise DSLSyntaxError
        with pytest.raises(DSLSyntaxError):
            Query("status")
        
        # Unknown operator - should raise UnknownOperatorError
        with pytest.raises(UnknownOperatorError):
            Query("status unknown_op value")
        
        # Missing value for operators that need it - should raise MissingValueError
        with pytest.raises(MissingValueError):
            Query("status equals")
        
        # All these are subclasses of DSLError
        with pytest.raises(DSLError):
            Query("status")
        
        # And all DSLErrors are ValueErrors
        with pytest.raises(ValueError):
            Query("invalid syntax here")
    
    def test_whitespace_handling(self):
        """Test that DSL handles various whitespace correctly."""
        data = {"status": "active", "count": 42}
        
        # Extra spaces
        q = Query("  status    equals    active  ")
        assert q.evaluate(data) is True
        
        # Tabs and newlines (normalized to spaces)
        q = Query("status\tequals\tactive")
        assert q.evaluate(data) is True
        
        # Multiple spaces in logical expressions
        q = Query("( status equals active )  and  ( count greater 40 )")
        assert q.evaluate(data) is True
    
    def test_case_sensitivity(self):
        """Test case handling in DSL."""
        data = {"status": "active", "Active": True}
        
        # Operators are case-insensitive
        q = Query("status EQUALS active")
        assert q.evaluate(data) is True
        
        q = Query("status EqUaLs active")
        assert q.evaluate(data) is True
        
        # But paths and values are case-sensitive
        q = Query("Status equals active")
        assert q.evaluate(data) is False  # 'Status' != 'status'
        
        q = Query("Active equals true")
        assert q.evaluate(data) is True  # 'Active' field exists


class TestDSLRealWorldExamples:
    """Test DSL with real-world use cases."""
    
    def test_user_permission_check(self):
        """Test complex permission checking."""
        user = {
            "username": "alice",
            "role": "editor",
            "permissions": ["read", "write", "delete"],
            "verified": True,
            "account": {
                "status": "active",
                "tier": "premium",
                "created_year": 2020
            }
        }
        
        # Can user delete? (admin OR (editor AND verified AND premium))
        q = Query("""
            (role equals admin) or 
            ((role equals editor) and (verified equals true) and (account.tier equals premium))
        """)
        assert q.evaluate(user) is True
        
        # Is trusted user? (verified AND active AND account age > 2 years)
        q = Query("""
            (verified equals true) and 
            (account.status equals active) and 
            (account.created_year less 2022)
        """)
        assert q.evaluate(user) is True
    
    def test_product_filtering(self):
        """Test product filtering scenarios."""
        product = {
            "name": "Premium Laptop",
            "price": 1299.99,
            "category": "electronics",
            "tags": ["laptop", "premium", "portable"],
            "inventory": {
                "inStock": True,
                "quantity": 15,
                "warehouse": "west"
            },
            "ratings": [4.5, 4.8, 4.2, 4.9]
        }
        
        # In stock AND reasonably priced
        q = Query("(inventory.inStock equals true) and (price less 1500)")
        assert q.evaluate(product) is True
        
        # Premium electronics with good stock
        q = Query("""
            (category equals electronics) and 
            (tags contains premium) and 
            (inventory.quantity greater 10)
        """)
        assert q.evaluate(product) is True
        
        # High-rated product (all ratings > 4.0)
        q = Query("all ratings greater 4.0")
        assert q.evaluate(product) is True
    
    def test_log_filtering(self):
        """Test log entry filtering."""
        log_entry = {
            "timestamp": "2024-01-15T10:30:00",
            "level": "ERROR",
            "service": "api-gateway",
            "message": "Connection timeout to database",
            "metadata": {
                "request_id": "abc-123",
                "user_id": "user-456",
                "retry_count": 3,
                "tags": ["database", "timeout", "critical"]
            }
        }
        
        # Critical errors
        q = Query("(level equals ERROR) and (metadata.tags contains critical)")
        assert q.evaluate(log_entry) is True
        
        # Database issues with retries
        q = Query("""
            (message contains database) and 
            (metadata.retry_count greater 2)
        """)
        assert q.evaluate(log_entry) is True
        
        # API gateway errors
        q = Query("(service equals api-gateway) and (level not_equals INFO)")
        assert q.evaluate(log_entry) is True
    
    def test_configuration_validation(self):
        """Test configuration validation scenarios."""
        config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "ssl": True,
                "pool": {
                    "min": 5,
                    "max": 20
                }
            },
            "cache": {
                "enabled": True,
                "ttl": 3600,
                "provider": "redis"
            },
            "features": ["auth", "logging", "metrics"]
        }
        
        # Valid database configuration
        q = Query("""
            (database.ssl equals true) and 
            (database.pool.min greater 0) and 
            (database.pool.max less 100)
        """)
        assert q.evaluate(config) is True
        
        # Cache properly configured
        q = Query("""
            (cache.enabled equals true) and 
            (cache.ttl greater 0) and 
            (cache.provider not_equals none)
        """)
        assert q.evaluate(config) is True
        
        # Required features enabled
        q = Query("(features contains auth) and (features contains logging)")
        assert q.evaluate(config) is True


class TestDSLAdvancedFeatures:
    """Test advanced DSL features and patterns."""
    
    def test_nested_quantifiers(self):
        """Test nested quantifier scenarios."""
        data = {
            "departments": [
                {
                    "name": "Engineering",
                    "employees": [
                        {"name": "Alice", "senior": True},
                        {"name": "Bob", "senior": True}
                    ]
                },
                {
                    "name": "Marketing",
                    "employees": [
                        {"name": "Charlie", "senior": False},
                        {"name": "David", "senior": True}
                    ]
                }
            ]
        }
        
        # At least one department has all senior employees
        # This would need more complex nesting support, but we can check each dept
        eng_data = {"employees": data["departments"][0]["employees"]}
        q = Query("all employees.senior equals true")
        assert q.evaluate(eng_data) is True
        
        mkt_data = {"employees": data["departments"][1]["employees"]}
        assert q.evaluate(mkt_data) is False
    
    def test_special_characters_in_values(self):
        """Test handling of special characters in values."""
        data = {
            "email": "user@example.com",
            "path": "/home/user/file.txt",
            "regex": "^[a-z]+$",
            "quote": "He said 'hello'"
        }
        
        # Values with special regex characters
        q = Query("email equals user@example.com")
        assert q.evaluate(data) is True
        
        # Path with slashes
        q = Query('path equals "/home/user/file.txt"')
        assert q.evaluate(data) is True
        
        # Regex pattern as value
        q = Query('regex equals "^[a-z]+$"')
        assert q.evaluate(data) is True
        
        # Quotes in values
        q = Query("""quote equals "He said 'hello'" """)
        assert q.evaluate(data) is True
    
    def test_performance_patterns(self):
        """Test patterns that might affect performance."""
        # Large collection
        data = {
            "items": list(range(1000)),
            "users": [{"id": i, "active": i % 2 == 0} for i in range(100)]
        }
        
        # Early termination with any
        q = Query("any items greater 500")
        assert q.evaluate(data) is True  # Should stop early
        
        # Full scan with all
        q = Query("all items less 1001")
        assert q.evaluate(data) is True  # Must check all
        
        # Complex path with wildcards
        q = Query("any users.active equals true")
        assert q.evaluate(data) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])