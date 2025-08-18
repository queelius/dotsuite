"""
Tests for dotquery - Truth pillar's compositional logic engine.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from truth.dotquery.core import Q, Query, Condition, And, Or, Not, Expression
import operator


class TestQBuilder:
    """Test the Q fluent query builder."""
    
    def test_q_equals(self):
        """Test Q equals queries."""
        data = {"status": "active", "count": 42}
        
        q = Q("status").equals("active")
        assert q.evaluate(data) is True
        
        q = Q("status").equals("inactive")
        assert q.evaluate(data) is False
        
        q = Q("count").equals(42)
        assert q.evaluate(data) is True
    
    def test_q_not_equals(self):
        """Test Q not_equals queries."""
        data = {"status": "active", "count": 42}
        
        q = Q("status").not_equals("inactive")
        assert q.evaluate(data) is True
        
        q = Q("status").not_equals("active")
        assert q.evaluate(data) is False
    
    def test_q_greater(self):
        """Test Q greater than queries."""
        data = {"age": 25, "score": 85.5}
        
        q = Q("age").greater(20)
        assert q.evaluate(data) is True
        
        q = Q("age").greater(30)
        assert q.evaluate(data) is False
        
        q = Q("score").greater(80)
        assert q.evaluate(data) is True
    
    def test_q_less(self):
        """Test Q less than queries."""
        data = {"age": 25, "score": 85.5}
        
        q = Q("age").less(30)
        assert q.evaluate(data) is True
        
        q = Q("age").less(20)
        assert q.evaluate(data) is False
        
        q = Q("score").less(90)
        assert q.evaluate(data) is True
    
    def test_q_contains(self):
        """Test Q contains queries."""
        data = {"tags": ["python", "data", "ml"], "name": "Alice Smith"}
        
        q = Q("tags").contains("python")
        assert q.evaluate(data) is True
        
        q = Q("tags").contains("java")
        assert q.evaluate(data) is False
        
        q = Q("name").contains("Smith")
        assert q.evaluate(data) is True
    
    def test_q_matches(self):
        """Test Q regex matching."""
        data = {"email": "alice@example.com", "phone": "123-456-7890"}
        
        q = Q("email").matches(r".*@example\.com")
        assert q.evaluate(data) is True
        
        q = Q("phone").matches(r"\d{3}-\d{3}-\d{4}")
        assert q.evaluate(data) is True
        
        q = Q("email").matches(r".*@gmail\.com")
        assert q.evaluate(data) is False


class TestLogicalOperators:
    """Test logical operator combinations."""
    
    def test_and_operator(self):
        """Test AND operator combination."""
        data = {"status": "active", "age": 25, "role": "admin"}
        
        q = Q("status").equals("active") & Q("age").greater(20)
        assert q.evaluate(data) is True
        
        q = Q("status").equals("active") & Q("age").greater(30)
        assert q.evaluate(data) is False
        
        # Triple AND
        q = Q("role").equals("admin") & Q("status").equals("active") & Q("age").less(30)
        assert q.evaluate(data) is True
    
    def test_or_operator(self):
        """Test OR operator combination."""
        data = {"status": "pending", "priority": "high"}
        
        q = Q("status").equals("active") | Q("priority").equals("high")
        assert q.evaluate(data) is True
        
        q = Q("status").equals("active") | Q("priority").equals("low")
        assert q.evaluate(data) is False
    
    def test_not_operator(self):
        """Test NOT operator."""
        data = {"status": "active", "verified": False}
        
        q = ~Q("status").equals("inactive")
        assert q.evaluate(data) is True
        
        q = ~Q("status").equals("active")
        assert q.evaluate(data) is False
    
    def test_complex_combinations(self):
        """Test complex logical combinations."""
        data = {
            "user": {"role": "admin", "active": True, "age": 35},
            "permissions": ["read", "write", "delete"]
        }
        
        # Admin with write permissions
        q = Q("user.role").equals("admin") & Q("permissions").contains("write")
        assert q.evaluate(data) is True
        
        # Active admin or has delete permission
        q = (Q("user.role").equals("admin") & Q("user.active").equals(True)) | Q("permissions").contains("delete")
        assert q.evaluate(data) is True
        
        # Young user or admin
        q = Q("user.age").less(30) | Q("user.role").equals("admin")
        assert q.evaluate(data) is True


class TestQuantifiers:
    """Test all/any quantifiers on collections."""
    
    def test_any_quantifier_default(self):
        """Test that any is the default quantifier."""
        data = {"scores": [70, 85, 92]}
        
        # By default, uses 'any' - at least one score > 80
        q = Q("scores").greater(80)
        assert q.evaluate(data) is True
        
        # None of the scores > 95
        q = Q("scores").greater(95)
        assert q.evaluate(data) is False
    
    def test_all_quantifier(self):
        """Test the all quantifier."""
        data = {"scores": [70, 85, 92]}
        
        # All scores > 60
        q = Q("scores").all().greater(60)
        assert q.evaluate(data) is True
        
        # Not all scores > 80
        q = Q("scores").all().greater(80)
        assert q.evaluate(data) is False
    
    def test_quantifiers_with_nested_paths(self):
        """Test quantifiers on nested collections."""
        data = {
            "users": [
                {"name": "Alice", "active": True},
                {"name": "Bob", "active": True},
                {"name": "Charlie", "active": False}
            ]
        }
        
        # Any user is active (default)
        q = Q("users.active").equals(True)
        assert q.evaluate(data) is True
        
        # All users are active
        q = Q("users.active").all().equals(True)
        assert q.evaluate(data) is False


class TestConditionClass:
    """Test the Condition class directly."""
    
    def test_condition_basic(self):
        """Test basic Condition operations."""
        data = {"value": 42}
        
        cond = Condition("value", operator.eq, 42)
        assert cond.evaluate(data) is True
        
        cond = Condition("value", operator.gt, 40)
        assert cond.evaluate(data) is True
        
        cond = Condition("value", operator.lt, 40)
        assert cond.evaluate(data) is False
    
    def test_condition_with_quantifier(self):
        """Test Condition with custom quantifier."""
        data = {"items": [1, 2, 3, 4, 5]}
        
        # Any item > 3 (default)
        cond = Condition("items", operator.gt, 3, quantifier=any)
        assert cond.evaluate(data) is True
        
        # All items > 0
        cond = Condition("items", operator.gt, 0, quantifier=all)
        assert cond.evaluate(data) is True
        
        # All items > 3
        cond = Condition("items", operator.gt, 3, quantifier=all)
        assert cond.evaluate(data) is False


class TestNestedPaths:
    """Test queries on nested data structures."""
    
    def test_nested_object_queries(self):
        """Test queries on nested objects."""
        data = {
            "profile": {
                "personal": {
                    "name": "Alice",
                    "age": 30
                },
                "professional": {
                    "title": "Engineer",
                    "years": 5
                }
            }
        }
        
        q = Q("profile.personal.name").equals("Alice")
        assert q.evaluate(data) is True
        
        q = Q("profile.professional.years").greater(3)
        assert q.evaluate(data) is True
        
        # Missing path returns False
        q = Q("profile.personal.email").equals("test@example.com")
        assert q.evaluate(data) is False
    
    def test_array_element_queries(self):
        """Test queries on array elements."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "scores": [85, 92, 78]
        }
        
        q = Q("users.0.name").equals("Alice")
        assert q.evaluate(data) is True
        
        q = Q("users.1.age").less(30)
        assert q.evaluate(data) is True
        
        q = Q("scores.1").greater(90)
        assert q.evaluate(data) is True


class TestExpressionComposition:
    """Test composing Expression objects directly."""
    
    def test_and_expression(self):
        """Test And expression."""
        data = {"a": 10, "b": 20}
        
        expr = And(
            Condition("a", operator.gt, 5),
            Condition("b", operator.lt, 30)
        )
        assert expr.evaluate(data) is True
        
        expr = And(
            Condition("a", operator.gt, 15),
            Condition("b", operator.lt, 30)
        )
        assert expr.evaluate(data) is False
    
    def test_or_expression(self):
        """Test Or expression."""
        data = {"a": 10, "b": 20}
        
        expr = Or(
            Condition("a", operator.gt, 15),
            Condition("b", operator.eq, 20)
        )
        assert expr.evaluate(data) is True
        
        expr = Or(
            Condition("a", operator.gt, 15),
            Condition("b", operator.lt, 10)
        )
        assert expr.evaluate(data) is False
    
    def test_not_expression(self):
        """Test Not expression."""
        data = {"value": 42}
        
        expr = Not(Condition("value", operator.eq, 0))
        assert expr.evaluate(data) is True
        
        expr = Not(Condition("value", operator.eq, 42))
        assert expr.evaluate(data) is False
    
    def test_nested_expressions(self):
        """Test nested expression composition."""
        data = {"a": 10, "b": 20, "c": 30}
        
        # (a > 5 AND b < 25) OR c == 30
        expr = Or(
            And(
                Condition("a", operator.gt, 5),
                Condition("b", operator.lt, 25)
            ),
            Condition("c", operator.eq, 30)
        )
        assert expr.evaluate(data) is True


class TestQueryMethods:
    """Test Query class methods."""
    
    def test_query_call(self):
        """Test calling Query as a function."""
        data = {"value": 42}
        
        q = Q("value").equals(42)
        # Can call query like a function
        assert q(data) is True
        
        q = Q("value").greater(50)
        assert q(data) is False
    
    def test_query_filter(self):
        """Test Query.filter method."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35}
        ]
        
        q = Q("age").greater(28)
        results = list(q.filter(data))
        assert len(results) == 2
        assert results[0]["name"] == "Alice"
        assert results[1]["name"] == "Charlie"


class TestEdgeCases:
    """Test edge cases and special values."""
    
    def test_query_with_none_values(self):
        """Test queries with None values."""
        data = {"value": None, "status": "active"}
        
        q = Q("value").equals(None)
        assert q.evaluate(data) is True
        
        q = Q("value").not_equals(None)
        assert q.evaluate(data) is False
    
    def test_query_with_boolean_values(self):
        """Test queries with boolean values."""
        data = {"active": True, "verified": False}
        
        q = Q("active").equals(True)
        assert q.evaluate(data) is True
        
        q = Q("verified").equals(False)
        assert q.evaluate(data) is True
        
        q = Q("active").not_equals(False)
        assert q.evaluate(data) is True
    
    def test_query_with_empty_collections(self):
        """Test queries with empty collections."""
        data = {"items": [], "options": {}}
        
        # Empty list doesn't contain anything
        q = Q("items").contains("something")
        assert q.evaluate(data) is False
        
        # All items in empty list satisfy any condition (vacuous truth)
        q = Q("items").all().greater(0)
        assert q.evaluate(data) is True
    
    def test_missing_paths(self):
        """Test behavior with missing paths."""
        data = {"value": 42}
        
        # Missing path comparisons return False
        q = Q("missing").equals(42)
        assert q.evaluate(data) is False
        
        q = Q("nested.missing.path").greater(0)
        assert q.evaluate(data) is False


class TestRealWorldScenarios:
    """Test real-world query scenarios."""
    
    def test_user_authorization(self):
        """Test user authorization queries."""
        user = {
            "username": "alice",
            "role": "editor",
            "permissions": ["read", "write", "edit"],
            "account": {
                "status": "active",
                "verified": True,
                "created_at": "2024-01-01"
            }
        }
        
        # Can edit if editor with active account
        q = Q("role").equals("editor") & Q("account.status").equals("active")
        assert q.evaluate(user) is True
        
        # Can delete if admin or has delete permission
        q = Q("role").equals("admin") | Q("permissions").contains("delete")
        assert q.evaluate(user) is False
        
        # Can access if verified and active
        q = Q("account.verified").equals(True) & Q("account.status").equals("active")
        assert q.evaluate(user) is True
    
    def test_product_filtering(self):
        """Test product filtering queries."""
        product = {
            "name": "Laptop",
            "price": 999.99,
            "category": "electronics",
            "tags": ["portable", "computer", "tech"],
            "specs": {
                "ram": 16,
                "storage": 512,
                "battery_hours": 10
            }
        }
        
        # High-value electronics
        q = Q("category").equals("electronics") & Q("price").greater(500)
        assert q.evaluate(product) is True
        
        # Portable with good battery
        q = Q("tags").contains("portable") & Q("specs.battery_hours").greater(8)
        assert q.evaluate(product) is True
        
        # Gaming laptop (high RAM and storage)
        q = Q("specs.ram").greater(12) & Q("specs.storage").greater(256)
        assert q.evaluate(product) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])