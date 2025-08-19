"""
Tests for dotrelate - Collections pillar relational operations.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/collections'))

from dotrelate.core import left_join, inner_join, project, union, set_difference


class TestLeftJoin:
    """Test left join operations."""
    
    def test_basic_left_join(self):
        """Test basic left join on collections."""
        users = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"}
        ]
        
        orders = [
            {"user_id": 1, "product": "Book"},
            {"user_id": 2, "product": "Pen"},
            {"user_id": 1, "product": "Notebook"}
        ]
        
        result = list(left_join(users, orders, "id", "user_id"))
        
        # Alice has 2 orders, so appears twice
        assert len(result) == 4
        assert result[0] == {"id": 1, "name": "Alice", "user_id": 1, "product": "Book"}
        assert result[1] == {"id": 1, "name": "Alice", "user_id": 1, "product": "Notebook"}
        # Bob gets his order
        assert result[2] == {"id": 2, "name": "Bob", "user_id": 2, "product": "Pen"}
        # Charlie has no orders
        assert result[3] == {"id": 3, "name": "Charlie"}
    
    def test_left_join_no_matches(self):
        """Test left join with no matching records."""
        left = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        
        right = [
            {"ref_id": 10, "value": "X"},
            {"ref_id": 20, "value": "Y"}
        ]
        
        result = list(left_join(left, right, "id", "ref_id"))
        
        # All left records preserved, no right data added
        assert result[0] == {"id": 1, "name": "Alice"}
        assert result[1] == {"id": 2, "name": "Bob"}
    
    def test_left_join_multiple_matches(self):
        """Test that left join returns all matching combinations."""
        departments = [
            {"dept_id": 1, "dept_name": "Engineering"}
        ]
        
        employees = [
            {"dept_id": 1, "emp_name": "Alice"},
            {"dept_id": 1, "emp_name": "Bob"},
            {"dept_id": 1, "emp_name": "Charlie"}
        ]
        
        result = list(left_join(departments, employees, "dept_id", "dept_id"))
        
        # All 3 employees match the department
        assert len(result) == 3
        assert result[0] == {"dept_id": 1, "dept_name": "Engineering", "emp_name": "Alice"}
        assert result[1] == {"dept_id": 1, "dept_name": "Engineering", "emp_name": "Bob"}
        assert result[2] == {"dept_id": 1, "dept_name": "Engineering", "emp_name": "Charlie"}
    
    def test_left_join_empty_collections(self):
        """Test left join with empty collections."""
        left = []
        right = [{"id": 1, "value": "test"}]
        
        result = list(left_join(left, right, "id", "id"))
        assert result == []
        
        left = [{"id": 1, "name": "Alice"}]
        right = []
        
        result = list(left_join(left, right, "id", "id"))
        assert result == [{"id": 1, "name": "Alice"}]
    
    def test_left_join_missing_keys(self):
        """Test left join when keys are missing."""
        left = [
            {"id": 1, "name": "Alice"},
            {"name": "Bob"}  # Missing id
        ]
        
        right = [
            {"ref_id": 1, "value": "X"}
        ]
        
        result = list(left_join(left, right, "id", "ref_id"))
        
        assert result[0] == {"id": 1, "name": "Alice", "ref_id": 1, "value": "X"}
        assert result[1] == {"name": "Bob"}  # No match due to missing id


class TestInnerJoin:
    """Test inner join operations."""
    
    def test_basic_inner_join(self):
        """Test basic inner join on collections."""
        users = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"}
        ]
        
        orders = [
            {"user_id": 1, "product": "Book"},
            {"user_id": 2, "product": "Pen"},
            {"user_id": 1, "product": "Notebook"}
        ]
        
        result = list(inner_join(users, orders, "id", "user_id"))
        
        # Only users with orders appear (no Charlie)
        assert len(result) == 3
        assert result[0] == {"id": 1, "name": "Alice", "user_id": 1, "product": "Book"}
        assert result[1] == {"id": 1, "name": "Alice", "user_id": 1, "product": "Notebook"}
        assert result[2] == {"id": 2, "name": "Bob", "user_id": 2, "product": "Pen"}
    
    def test_inner_join_no_matches(self):
        """Test inner join with no matching records."""
        left = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        
        right = [
            {"ref_id": 10, "value": "X"},
            {"ref_id": 20, "value": "Y"}
        ]
        
        result = list(inner_join(left, right, "id", "ref_id"))
        
        # No matches, empty result
        assert result == []
    
    def test_inner_join_empty_collections(self):
        """Test inner join with empty collections."""
        left = []
        right = [{"id": 1, "value": "test"}]
        
        result = list(inner_join(left, right, "id", "id"))
        assert result == []
        
        left = [{"id": 1, "name": "Alice"}]
        right = []
        
        result = list(inner_join(left, right, "id", "id"))
        assert result == []


class TestProject:
    """Test projection operations."""
    
    def test_basic_projection(self):
        """Test basic field projection."""
        data = [
            {"id": 1, "name": "Alice", "age": 30, "city": "NYC"},
            {"id": 2, "name": "Bob", "age": 25, "city": "LA"}
        ]
        
        result = list(project(data, ["name", "age"]))
        
        assert result[0] == {"name": "Alice", "age": 30}
        assert result[1] == {"name": "Bob", "age": 25}
    
    def test_project_missing_fields(self):
        """Test projection with missing fields."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
        
        result = list(project(data, ["name", "email"]))
        
        assert result[0] == {"name": "Alice", "email": None}
        assert result[1] == {"name": "Bob", "email": "bob@example.com"}
    
    def test_project_empty_fields(self):
        """Test projection with empty field list."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        
        result = list(project(data, []))
        
        assert result[0] == {}
        assert result[1] == {}
    
    def test_project_empty_collection(self):
        """Test projection on empty collection."""
        result = list(project([], ["name", "age"]))
        assert result == []
    
    def test_project_single_field(self):
        """Test projection of single field."""
        data = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25}
        ]
        
        result = list(project(data, ["name"]))
        
        assert result[0] == {"name": "Alice"}
        assert result[1] == {"name": "Bob"}


class TestUnion:
    """Test union operations."""
    
    def test_basic_union(self):
        """Test basic union of two collections."""
        left = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        
        right = [
            {"id": 3, "name": "Charlie"},
            {"id": 4, "name": "David"}
        ]
        
        result = list(union(left, right))
        
        assert len(result) == 4
        assert result[0] == {"id": 1, "name": "Alice"}
        assert result[1] == {"id": 2, "name": "Bob"}
        assert result[2] == {"id": 3, "name": "Charlie"}
        assert result[3] == {"id": 4, "name": "David"}
    
    def test_union_with_duplicates(self):
        """Test union preserves duplicates."""
        left = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        
        right = [
            {"id": 1, "name": "Alice"},  # Duplicate
            {"id": 3, "name": "Charlie"}
        ]
        
        result = list(union(left, right))
        
        assert len(result) == 4  # Duplicates preserved
        assert result[0] == {"id": 1, "name": "Alice"}
        assert result[2] == {"id": 1, "name": "Alice"}
    
    def test_union_empty_collections(self):
        """Test union with empty collections."""
        left = []
        right = [{"id": 1, "name": "Alice"}]
        
        result = list(union(left, right))
        assert result == [{"id": 1, "name": "Alice"}]
        
        left = [{"id": 1, "name": "Alice"}]
        right = []
        
        result = list(union(left, right))
        assert result == [{"id": 1, "name": "Alice"}]
        
        result = list(union([], []))
        assert result == []
    
    def test_union_different_schemas(self):
        """Test union with different schemas."""
        left = [
            {"id": 1, "name": "Alice"}
        ]
        
        right = [
            {"user_id": 2, "username": "Bob", "email": "bob@example.com"}
        ]
        
        result = list(union(left, right))
        
        assert len(result) == 2
        assert result[0] == {"id": 1, "name": "Alice"}
        assert result[1] == {"user_id": 2, "username": "Bob", "email": "bob@example.com"}


class TestSetDifference:
    """Test set difference operations."""
    
    def test_basic_set_difference(self):
        """Test basic set difference."""
        left = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"}
        ]
        
        right = [
            {"id": 2, "name": "Bob"}
        ]
        
        result = list(set_difference(left, right))
        
        assert len(result) == 2
        assert {"id": 1, "name": "Alice"} in result
        assert {"id": 3, "name": "Charlie"} in result
        assert {"id": 2, "name": "Bob"} not in result
    
    def test_set_difference_no_overlap(self):
        """Test set difference with no overlapping items."""
        left = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        
        right = [
            {"id": 3, "name": "Charlie"},
            {"id": 4, "name": "David"}
        ]
        
        result = list(set_difference(left, right))
        
        # All left items remain
        assert len(result) == 2
        assert result[0] == {"id": 1, "name": "Alice"}
        assert result[1] == {"id": 2, "name": "Bob"}
    
    def test_set_difference_complete_overlap(self):
        """Test set difference with complete overlap."""
        left = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        
        right = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        
        result = list(set_difference(left, right))
        assert result == []
    
    def test_set_difference_empty_collections(self):
        """Test set difference with empty collections."""
        left = [{"id": 1, "name": "Alice"}]
        right = []
        
        result = list(set_difference(left, right))
        assert result == [{"id": 1, "name": "Alice"}]
        
        left = []
        right = [{"id": 1, "name": "Alice"}]
        
        result = list(set_difference(left, right))
        assert result == []
    
    def test_set_difference_with_duplicates(self):
        """Test set difference handles duplicates."""
        left = [
            {"id": 1, "name": "Alice"},
            {"id": 1, "name": "Alice"},  # Duplicate
            {"id": 2, "name": "Bob"}
        ]
        
        right = [
            {"id": 1, "name": "Alice"}
        ]
        
        result = list(set_difference(left, right))
        
        # Both Alice entries removed
        assert len(result) == 1
        assert result[0] == {"id": 2, "name": "Bob"}
    
    def test_set_difference_complex_objects(self):
        """Test set difference with nested objects."""
        left = [
            {"id": 1, "user": {"name": "Alice", "age": 30}},
            {"id": 2, "user": {"name": "Bob", "age": 25}}
        ]
        
        right = [
            {"id": 1, "user": {"name": "Alice", "age": 30}}
        ]
        
        result = list(set_difference(left, right))
        
        assert len(result) == 1
        assert result[0] == {"id": 2, "user": {"name": "Bob", "age": 25}}


class TestRealWorldScenarios:
    """Test real-world usage patterns."""
    
    def test_user_order_analysis(self):
        """Test joining users with orders and projecting results."""
        users = [
            {"user_id": 1, "name": "Alice", "email": "alice@example.com"},
            {"user_id": 2, "name": "Bob", "email": "bob@example.com"},
            {"user_id": 3, "name": "Charlie", "email": "charlie@example.com"}
        ]
        
        orders = [
            {"order_id": 101, "user_id": 1, "amount": 50.00, "product": "Book"},
            {"order_id": 102, "user_id": 2, "amount": 25.00, "product": "Pen"}
        ]
        
        # Join users with orders
        joined = list(left_join(users, orders, "user_id", "user_id"))
        
        # Project relevant fields
        result = list(project(joined, ["name", "product", "amount"]))
        
        assert result[0] == {"name": "Alice", "product": "Book", "amount": 50.00}
        assert result[1] == {"name": "Bob", "product": "Pen", "amount": 25.00}
        assert result[2] == {"name": "Charlie", "product": None, "amount": None}
    
    def test_data_deduplication(self):
        """Test removing duplicates using set difference."""
        all_records = [
            {"id": 1, "email": "alice@example.com"},
            {"id": 2, "email": "bob@example.com"},
            {"id": 3, "email": "charlie@example.com"},
            {"id": 1, "email": "alice@example.com"},  # Duplicate
            {"id": 4, "email": "david@example.com"}
        ]
        
        seen = [
            {"id": 1, "email": "alice@example.com"}
        ]
        
        # Get unique records
        unique = list(set_difference(all_records, seen))
        
        assert len(unique) == 3
        assert {"id": 2, "email": "bob@example.com"} in unique
        assert {"id": 3, "email": "charlie@example.com"} in unique
        assert {"id": 4, "email": "david@example.com"} in unique
    
    def test_combining_data_sources(self):
        """Test combining multiple data sources."""
        source1 = [
            {"source": "api", "timestamp": "2024-01-01", "value": 100},
            {"source": "api", "timestamp": "2024-01-02", "value": 150}
        ]
        
        source2 = [
            {"source": "database", "timestamp": "2024-01-01", "value": 110},
            {"source": "database", "timestamp": "2024-01-03", "value": 200}
        ]
        
        # Combine all sources
        combined = list(union(source1, source2))
        
        assert len(combined) == 4
        assert combined[0]["source"] == "api"
        assert combined[2]["source"] == "database"
        
        # Project just the values
        values = list(project(combined, ["timestamp", "value"]))
        
        assert len(values) == 4
        assert all("source" not in v for v in values)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])