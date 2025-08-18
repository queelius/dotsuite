"""
Tests for dotstar - Depth pillar's wildcard pattern matching.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from depth.dotstar.core import search, find_all, Pattern


class TestBasicSearch:
    """Test basic search functionality."""
    
    def test_search_simple_wildcard(self):
        """Test searching with simple wildcards."""
        data = {"a": 1, "b": 2, "c": 3}
        
        # Wildcard matches all values
        result = search(data, "*")
        assert set(result) == {1, 2, 3}
    
    def test_search_list_wildcard(self):
        """Test wildcard search in lists."""
        data = {"items": [1, 2, 3, 4, 5]}
        
        result = search(data, "items.*")
        assert result == [1, 2, 3, 4, 5]
    
    def test_search_nested_wildcard(self):
        """Test wildcard in nested structures."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
                {"name": "Charlie", "age": 35}
            ]
        }
        
        # Get all names
        names = search(data, "users.*.name")
        assert names == ["Alice", "Bob", "Charlie"]
        
        # Get all ages
        ages = search(data, "users.*.age")
        assert ages == [30, 25, 35]
    
    def test_search_dict_wildcard(self):
        """Test wildcard matching dictionary keys."""
        data = {
            "dept_a": {"budget": 10000},
            "dept_b": {"budget": 15000},
            "dept_c": {"budget": 12000}
        }
        
        budgets = search(data, "*.budget")
        assert set(budgets) == {10000, 15000, 12000}
    
    def test_search_no_matches(self):
        """Test search with no matches."""
        data = {"a": 1, "b": 2}
        
        result = search(data, "c")
        assert result == []
        
        result = search(data, "*.missing")
        assert result == []
    
    def test_search_specific_path(self):
        """Test search without wildcards (like dotget)."""
        data = {"user": {"name": "Alice", "age": 30}}
        
        result = search(data, "user.name")
        assert result == ["Alice"]
        
        result = search(data, "user.age")
        assert result == [30]


class TestMultipleWildcards:
    """Test patterns with multiple wildcards."""
    
    def test_double_wildcard(self):
        """Test patterns with two wildcards."""
        data = {
            "teams": {
                "alpha": {"members": [{"name": "Alice"}, {"name": "Ann"}]},
                "beta": {"members": [{"name": "Bob"}, {"name": "Bill"}]}
            }
        }
        
        # All member names across all teams
        names = search(data, "teams.*.members.*.name")
        assert set(names) == {"Alice", "Ann", "Bob", "Bill"}
    
    def test_wildcard_at_different_levels(self):
        """Test wildcards at different nesting levels."""
        data = {
            "regions": [
                {
                    "name": "North",
                    "stores": [
                        {"id": 1, "sales": 1000},
                        {"id": 2, "sales": 1500}
                    ]
                },
                {
                    "name": "South",
                    "stores": [
                        {"id": 3, "sales": 2000},
                        {"id": 4, "sales": 1200}
                    ]
                }
            ]
        }
        
        # All store sales across all regions
        sales = search(data, "regions.*.stores.*.sales")
        assert set(sales) == {1000, 1500, 2000, 1200}
    
    def test_consecutive_wildcards(self):
        """Test consecutive wildcards."""
        data = {"a": {"b": {"c": 1, "d": 2}, "e": {"c": 3, "d": 4}}}
        
        # *.* should get all nested values
        result = search(data, "a.*.*")
        assert set(result) == {1, 2, 3, 4}


class TestFindAll:
    """Test find_all function that returns paths and values."""
    
    def test_find_all_basic(self):
        """Test find_all returns paths and values."""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        
        result = find_all(data, "users.*.name")
        assert result == [
            ("users.0.name", "Alice"),
            ("users.1.name", "Bob")
        ]
    
    def test_find_all_dict_wildcard(self):
        """Test find_all with dictionary wildcards."""
        data = {
            "dept_a": {"budget": 10000},
            "dept_b": {"budget": 15000}
        }
        
        result = find_all(data, "*.budget")
        # Convert to set for order-independent comparison
        result_set = set(result)
        expected_set = {
            ("dept_a.budget", 10000),
            ("dept_b.budget", 15000)
        }
        assert result_set == expected_set
    
    def test_find_all_no_matches(self):
        """Test find_all with no matches."""
        data = {"a": 1}
        
        result = find_all(data, "b")
        assert result == []
    
    def test_find_all_nested(self):
        """Test find_all with nested structures."""
        data = {
            "company": {
                "departments": [
                    {"name": "Engineering", "head": "Alice"},
                    {"name": "Sales", "head": "Bob"}
                ]
            }
        }
        
        result = find_all(data, "company.departments.*.head")
        assert result == [
            ("company.departments.0.head", "Alice"),
            ("company.departments.1.head", "Bob")
        ]


class TestPatternClass:
    """Test the Pattern class."""
    
    def test_pattern_creation(self):
        """Test creating Pattern objects."""
        p = Pattern("users.*.name")
        assert str(p) == "users.*.name"
    
    def test_pattern_search(self):
        """Test searching with Pattern objects."""
        data = {"items": [{"id": 1}, {"id": 2}, {"id": 3}]}
        
        p = Pattern("items.*.id")
        result = p.search(data)
        assert result == [1, 2, 3]
    
    def test_pattern_find_all(self):
        """Test find_all with Pattern objects."""
        data = {"a": 1, "b": 2}
        
        p = Pattern("*")
        result = p.find_all(data)
        assert set(result) == {("a", 1), ("b", 2)}
    
    def test_pattern_composition(self):
        """Test composing patterns."""
        # Start with users pattern
        users = Pattern("users.*")
        
        # Extend to get emails
        emails = users / "email"
        assert str(emails) == "users.*.email"
        
        # Test it works
        data = {
            "users": [
                {"email": "alice@example.com"},
                {"email": "bob@example.com"}
            ]
        }
        result = emails.search(data)
        assert result == ["alice@example.com", "bob@example.com"]


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_empty_pattern(self):
        """Test empty pattern."""
        data = {"a": 1}
        
        # Empty pattern returns empty list (no path to follow)
        result = search(data, "")
        assert result == []
    
    def test_empty_data(self):
        """Test searching in empty structures."""
        assert search({}, "*") == []
        assert search([], "*") == []
        assert search(None, "*") == []
    
    def test_none_values(self):
        """Test searching for None values."""
        data = {"a": None, "b": None, "c": 1}
        
        result = search(data, "*")
        assert None in result
        assert result.count(None) == 2
        assert 1 in result
    
    def test_mixed_types(self):
        """Test with mixed data types."""
        data = {
            "values": [1, "two", 3.0, True, None, {"nested": "value"}]
        }
        
        result = search(data, "values.*")
        assert len(result) == 6
        assert 1 in result
        assert "two" in result
        assert 3.0 in result
        assert True in result
        assert None in result
        assert {"nested": "value"} in result
    
    def test_deeply_nested(self):
        """Test with deeply nested structures."""
        data = {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        
        result = search(data, "a.b.c.d.e")
        assert result == ["deep"]
        
        # Wildcard at deep level
        result = search(data, "a.b.c.d.*")
        assert result == ["deep"]
    
    def test_list_indices(self):
        """Test specific list indices."""
        data = {"items": ["a", "b", "c", "d"]}
        
        result = search(data, "items.0")
        assert result == ["a"]
        
        result = search(data, "items.2")
        assert result == ["c"]
        
        # Out of bounds
        result = search(data, "items.10")
        assert result == []


class TestRealWorldScenarios:
    """Test real-world usage patterns."""
    
    def test_extract_all_emails(self):
        """Test extracting all emails from nested structure."""
        data = {
            "departments": {
                "engineering": {
                    "teams": [
                        {"members": [{"email": "alice@example.com"}, {"email": "ann@example.com"}]},
                        {"members": [{"email": "alex@example.com"}]}
                    ]
                },
                "sales": {
                    "teams": [
                        {"members": [{"email": "bob@example.com"}, {"email": "bill@example.com"}]}
                    ]
                }
            }
        }
        
        emails = search(data, "departments.*.teams.*.members.*.email")
        assert len(emails) == 5
        assert all("@example.com" in email for email in emails)
    
    def test_aggregate_metrics(self):
        """Test aggregating metrics from multiple sources."""
        data = {
            "servers": [
                {"name": "server1", "metrics": {"cpu": 45, "memory": 67}},
                {"name": "server2", "metrics": {"cpu": 78, "memory": 89}},
                {"name": "server3", "metrics": {"cpu": 23, "memory": 45}}
            ]
        }
        
        # Get all CPU values
        cpu_values = search(data, "servers.*.metrics.cpu")
        assert cpu_values == [45, 78, 23]
        
        # Get all memory values
        memory_values = search(data, "servers.*.metrics.memory")
        assert memory_values == [67, 89, 45]
    
    def test_find_all_errors(self):
        """Test finding all error messages in logs."""
        data = {
            "logs": {
                "2024-01-01": [
                    {"level": "INFO", "message": "Started"},
                    {"level": "ERROR", "message": "Connection failed"},
                    {"level": "INFO", "message": "Retrying"}
                ],
                "2024-01-02": [
                    {"level": "ERROR", "message": "Timeout"},
                    {"level": "INFO", "message": "Success"}
                ]
            }
        }
        
        # Get all messages from all dates
        all_messages = search(data, "logs.*.*.message")
        assert len(all_messages) == 5
        assert "Connection failed" in all_messages
        assert "Timeout" in all_messages
    
    def test_product_variations(self):
        """Test finding all product variations."""
        data = {
            "products": [
                {
                    "name": "T-Shirt",
                    "variations": [
                        {"size": "S", "price": 19.99},
                        {"size": "M", "price": 19.99},
                        {"size": "L", "price": 21.99}
                    ]
                },
                {
                    "name": "Hoodie",
                    "variations": [
                        {"size": "M", "price": 39.99},
                        {"size": "L", "price": 39.99}
                    ]
                }
            ]
        }
        
        # Get all prices
        prices = search(data, "products.*.variations.*.price")
        assert len(prices) == 5
        assert prices.count(19.99) == 2
        assert prices.count(21.99) == 1
        assert prices.count(39.99) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])