"""
Tests for dotpipe - Shape pillar's transformation pipeline tool.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from shape.dotpipe.core import Pipeline, from_dsl, SAFE_FUNCTIONS


class TestPipelineBasics:
    """Test basic Pipeline functionality."""
    
    def test_pipeline_initialization(self):
        """Test creating a pipeline."""
        data = {"name": "Alice", "age": 30}
        
        pipeline = Pipeline(data)
        result = pipeline.apply()
        
        assert result == {"name": "Alice", "age": 30}
        # Original unchanged
        assert data == {"name": "Alice", "age": 30}
    
    def test_pipeline_requires_dict(self):
        """Test that Pipeline requires a dictionary."""
        with pytest.raises(TypeError, match="only be initialized with a dictionary"):
            Pipeline([1, 2, 3])
        
        with pytest.raises(TypeError, match="only be initialized with a dictionary"):
            Pipeline("not a dict")
    
    def test_pipeline_immutability(self):
        """Test that pipeline doesn't modify original data."""
        data = {"user": {"name": "Alice", "age": 30}}
        
        pipeline = Pipeline(data)
        pipeline.assign("userName", from_path="user.name")
        result = pipeline.apply()
        
        assert "userName" in result
        assert "userName" not in data


class TestAssign:
    """Test the assign method."""
    
    def test_assign_simple_path(self):
        """Test assigning from simple paths."""
        data = {"user": {"name": "Alice", "age": 30}}
        
        pipeline = Pipeline(data)
        result = pipeline.assign("userName", from_path="user.name").apply()
        
        assert result["userName"] == "Alice"
        assert "user" in result  # Original fields preserved
    
    def test_assign_with_function(self):
        """Test assigning with transformation function."""
        data = {"user": {"name": "alice"}}
        
        pipeline = Pipeline(data)
        result = pipeline.assign("upperName", from_path="user.name", then="upper").apply()
        
        assert result["upperName"] == "ALICE"
    
    def test_assign_with_function_chain(self):
        """Test assigning with multiple transformation functions."""
        data = {"items": [[1, 2], [3, 4], [5, 6]]}
        
        pipeline = Pipeline(data)
        result = pipeline.assign("flattened", from_path="items", then=["flatten", "unique"]).apply()
        
        assert result["flattened"] == [1, 2, 3, 4, 5, 6]
    
    def test_assign_with_callable(self):
        """Test assigning with custom callable."""
        data = {"value": 10}
        
        pipeline = Pipeline(data)
        result = pipeline.assign("doubled", from_path="value", then=lambda x: x * 2).apply()
        
        assert result["doubled"] == 20
    
    def test_assign_missing_path(self):
        """Test assigning from non-existent path."""
        data = {"a": 1}
        
        pipeline = Pipeline(data)
        result = pipeline.assign("missing", from_path="b.c.d").apply()
        
        assert result["missing"] is None
    
    def test_assign_wildcard_path(self):
        """Test assigning from wildcard paths."""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}, {"name": "Charlie"}]}
        
        pipeline = Pipeline(data)
        result = pipeline.assign("allNames", from_path="users.*.name").apply()
        
        assert result["allNames"] == ["Alice", "Bob", "Charlie"]


class TestPluck:
    """Test the pluck method."""
    
    def test_pluck_single_field(self):
        """Test plucking a single field."""
        data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
        
        pipeline = Pipeline(data)
        result = pipeline.pluck("name").apply()
        
        assert result == {"name": "Alice"}
    
    def test_pluck_multiple_fields(self):
        """Test plucking multiple fields."""
        data = {"name": "Alice", "age": 30, "email": "alice@example.com", "city": "NYC"}
        
        pipeline = Pipeline(data)
        result = pipeline.pluck("name", "email").apply()
        
        assert result == {"name": "Alice", "email": "alice@example.com"}
        assert "age" not in result
        assert "city" not in result
    
    def test_pluck_non_existent_fields(self):
        """Test plucking fields that don't exist."""
        data = {"name": "Alice", "age": 30}
        
        pipeline = Pipeline(data)
        result = pipeline.pluck("name", "missing").apply()
        
        assert result == {"name": "Alice"}
        assert "missing" not in result


class TestDelete:
    """Test the delete method."""
    
    def test_delete_single_field(self):
        """Test deleting a single field."""
        data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
        
        pipeline = Pipeline(data)
        result = pipeline.delete("email").apply()
        
        assert result == {"name": "Alice", "age": 30}
        assert "email" not in result
    
    def test_delete_multiple_fields(self):
        """Test deleting multiple fields."""
        data = {"name": "Alice", "age": 30, "email": "alice@example.com", "city": "NYC"}
        
        pipeline = Pipeline(data)
        result = pipeline.delete("age", "city").apply()
        
        assert result == {"name": "Alice", "email": "alice@example.com"}
    
    def test_delete_non_existent_fields(self):
        """Test deleting fields that don't exist."""
        data = {"name": "Alice"}
        
        pipeline = Pipeline(data)
        result = pipeline.delete("missing", "also_missing").apply()
        
        assert result == {"name": "Alice"}


class TestApplyTo:
    """Test the apply_to method."""
    
    def test_apply_to_existing_field(self):
        """Test applying function to existing field."""
        data = {"name": "alice", "age": 30}
        
        pipeline = Pipeline(data)
        result = pipeline.apply_to("name", "upper").apply()
        
        assert result == {"name": "ALICE", "age": 30}
    
    def test_apply_to_with_chain(self):
        """Test applying function chain to field."""
        data = {"text": "  hello world  "}
        
        pipeline = Pipeline(data)
        result = pipeline.apply_to("text", ["upper"]).apply()
        
        assert result["text"] == "  HELLO WORLD  "
    
    def test_apply_to_missing_field(self):
        """Test applying to non-existent field."""
        data = {"name": "Alice"}
        
        pipeline = Pipeline(data)
        result = pipeline.apply_to("missing", "upper").apply()
        
        assert result == {"name": "Alice"}
        assert "missing" not in result
    
    def test_apply_to_with_callable(self):
        """Test applying custom callable to field."""
        data = {"count": 5}
        
        pipeline = Pipeline(data)
        result = pipeline.apply_to("count", lambda x: x * 3).apply()
        
        assert result == {"count": 15}


class TestMethodChaining:
    """Test chaining multiple pipeline methods."""
    
    def test_complex_pipeline(self):
        """Test a complex pipeline with multiple operations."""
        data = {
            "user": {"firstName": "alice", "lastName": "smith", "age": 30},
            "items": [1, 2, 3, 4, 5],
            "metadata": {"created": "2024-01-01", "updated": "2024-01-15"}
        }
        
        pipeline = (Pipeline(data)
            .assign("fullName", from_path="user.firstName", then="upper")
            .assign("itemCount", from_path="items", then="len")
            .assign("totalSum", from_path="items", then="sum")
            .delete("metadata")
            .apply_to("fullName", lambda x: x + " SMITH")
            .pluck("fullName", "itemCount", "totalSum", "user"))
        
        result = pipeline.apply()
        
        assert result == {
            "fullName": "ALICE SMITH",
            "itemCount": 5,
            "totalSum": 15,
            "user": {"firstName": "alice", "lastName": "smith", "age": 30}
        }
    
    def test_pipeline_ordering(self):
        """Test that pipeline operations execute in order."""
        data = {"value": 10}
        
        # First double, then add 5
        pipeline1 = (Pipeline(data)
            .apply_to("value", lambda x: x * 2)
            .apply_to("value", lambda x: x + 5))
        
        assert pipeline1.apply() == {"value": 25}
        
        # First add 5, then double
        pipeline2 = (Pipeline({"value": 10})
            .apply_to("value", lambda x: x + 5)
            .apply_to("value", lambda x: x * 2))
        
        assert pipeline2.apply() == {"value": 30}


class TestSafeFunctions:
    """Test the built-in safe functions."""
    
    def test_safe_functions_available(self):
        """Test that safe functions are available."""
        assert "len" in SAFE_FUNCTIONS
        assert "sum" in SAFE_FUNCTIONS
        assert "upper" in SAFE_FUNCTIONS
        assert "lower" in SAFE_FUNCTIONS
        assert "flatten" in SAFE_FUNCTIONS
        assert "unique" in SAFE_FUNCTIONS
        assert "first" in SAFE_FUNCTIONS
        assert "last" in SAFE_FUNCTIONS
    
    def test_flatten_function(self):
        """Test the flatten function."""
        data = {"nested": [[1, 2], [3, 4], [5]]}
        
        pipeline = Pipeline(data)
        result = pipeline.assign("flat", from_path="nested", then="flatten").apply()
        
        assert result["flat"] == [1, 2, 3, 4, 5]
    
    def test_unique_function(self):
        """Test the unique function."""
        data = {"items": [1, 2, 2, 3, 1, 4, 3]}
        
        pipeline = Pipeline(data)
        result = pipeline.assign("unique_items", from_path="items", then="unique").apply()
        
        assert result["unique_items"] == [1, 2, 3, 4]
    
    def test_first_last_functions(self):
        """Test first and last functions."""
        data = {"items": [10, 20, 30, 40]}
        
        pipeline = Pipeline(data)
        result = (pipeline
            .assign("first_item", from_path="items", then="first")
            .assign("last_item", from_path="items", then="last")
            .apply())
        
        assert result["first_item"] == 10
        assert result["last_item"] == 40


class TestFromDSL:
    """Test the from_dsl function for declarative pipelines."""
    
    def test_dsl_basic(self):
        """Test basic DSL pipeline."""
        data = {"user": {"name": "alice"}, "count": 5}
        
        dsl = [
            {"verb": "assign", "field": "userName", "path": "user.name", "then": "upper"},
            {"verb": "delete", "fields": ["count"]}
        ]
        
        result = from_dsl(data, dsl)
        
        assert result["userName"] == "ALICE"
        assert "count" not in result
        assert "user" in result
    
    def test_dsl_pluck(self):
        """Test DSL with pluck."""
        data = {"a": 1, "b": 2, "c": 3, "d": 4}
        
        dsl = [
            {"verb": "pluck", "fields": ["a", "c"]}
        ]
        
        result = from_dsl(data, dsl)
        assert result == {"a": 1, "c": 3}
    
    def test_dsl_apply_to(self):
        """Test DSL with apply_to."""
        data = {"text": "hello"}
        
        dsl = [
            {"verb": "apply_to", "field": "text", "func": "upper"}
        ]
        
        result = from_dsl(data, dsl)
        assert result == {"text": "HELLO"}
    
    def test_dsl_complex_pipeline(self):
        """Test complex DSL pipeline."""
        data = {
            "products": [
                {"name": "laptop", "price": 999},
                {"name": "mouse", "price": 25},
                {"name": "keyboard", "price": 75}
            ]
        }
        
        dsl = [
            {"verb": "assign", "field": "prices", "path": "products.*.price"},
            {"verb": "assign", "field": "totalPrice", "path": "products.*.price", "then": "sum"},
            {"verb": "assign", "field": "productCount", "path": "products", "then": "len"},
            {"verb": "delete", "fields": ["products"]}
        ]
        
        result = from_dsl(data, dsl)
        
        assert result["prices"] == [999, 25, 75]
        assert result["totalPrice"] == 1099
        assert result["productCount"] == 3
        assert "products" not in result
    
    def test_dsl_missing_verb(self):
        """Test DSL validation for missing verb."""
        data = {"a": 1}
        
        dsl = [{"field": "b", "path": "a"}]  # Missing verb
        
        with pytest.raises(ValueError, match="must have a 'verb' key"):
            from_dsl(data, dsl)
    
    def test_dsl_unknown_verb(self):
        """Test DSL validation for unknown verb."""
        data = {"a": 1}
        
        dsl = [{"verb": "unknown_verb", "field": "b"}]
        
        with pytest.raises(ValueError, match="Unknown verb"):
            from_dsl(data, dsl)


class TestRealWorldScenarios:
    """Test real-world usage patterns."""
    
    def test_user_profile_transformation(self):
        """Test transforming user profile data."""
        data = {
            "user_id": 123,
            "first_name": "alice",
            "last_name": "smith",
            "email": "alice@example.com",
            "created_timestamp": 1704067200,
            "preferences": {
                "theme": "dark",
                "notifications": True
            },
            "activity": {
                "logins": [1, 2, 3, 4, 5],
                "posts": ["post1", "post2"]
            }
        }
        
        pipeline = (Pipeline(data)
            .assign("fullName", from_path="first_name", then="upper")
            .apply_to("fullName", lambda x: x + " SMITH")
            .assign("loginCount", from_path="activity.logins", then="len")
            .assign("postCount", from_path="activity.posts", then="len")
            .assign("isDarkMode", from_path="preferences.theme")
            .apply_to("isDarkMode", lambda x: x == "dark")
            .delete("created_timestamp", "activity", "first_name", "last_name")
            .pluck("user_id", "fullName", "email", "loginCount", "postCount", "isDarkMode"))
        
        result = pipeline.apply()
        
        assert result == {
            "user_id": 123,
            "fullName": "ALICE SMITH",
            "email": "alice@example.com",
            "loginCount": 5,
            "postCount": 2,
            "isDarkMode": True
        }
    
    def test_data_aggregation(self):
        """Test aggregating data from multiple sources."""
        data = {
            "sales": {
                "q1": [100, 150, 200],
                "q2": [180, 220, 250],
                "q3": [200, 240, 280],
                "q4": [250, 300, 350]
            },
            "expenses": {
                "q1": 300,
                "q2": 400,
                "q3": 450,
                "q4": 500
            }
        }
        
        pipeline = (Pipeline(data)
            .assign("q1_total", from_path="sales.q1", then="sum")
            .assign("q2_total", from_path="sales.q2", then="sum")
            .assign("q3_total", from_path="sales.q3", then="sum")
            .assign("q4_total", from_path="sales.q4", then="sum")
            .assign("annual_sales", from_path="sales.*", then=["flatten", "sum"])
            .assign("annual_expenses", from_path="expenses.*", then="sum")
            .apply_to("annual_expenses", lambda x: -x)  # Make negative
            .delete("sales", "expenses"))
        
        result = pipeline.apply()
        
        assert result["q1_total"] == 450
        assert result["q2_total"] == 650
        assert result["q3_total"] == 720
        assert result["q4_total"] == 900
        assert result["annual_sales"] == 2720
        assert result["annual_expenses"] == -1650


if __name__ == "__main__":
    pytest.main([__file__, "-v"])