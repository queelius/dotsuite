"""
Tests for dotbatch - Shape pillar's atomic transaction tool.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from shape.dotbatch.core import Batch, Operation, apply


class TestBatchBasics:
    """Test basic Batch functionality."""
    
    def test_batch_initialization(self):
        """Test creating a batch."""
        data = {"name": "Alice", "age": 30}
        
        batch = Batch(data)
        result = batch.apply()
        
        assert result == {"name": "Alice", "age": 30}
        # Original unchanged
        assert data == {"name": "Alice", "age": 30}
    
    def test_batch_empty_operations(self):
        """Test batch with no operations."""
        data = {"a": 1, "b": 2}
        
        batch = Batch(data)
        result = batch.apply()
        
        assert result == {"a": 1, "b": 2}
        assert result is not data  # Still a copy
    
    def test_batch_set_operation(self):
        """Test basic set operation in batch."""
        data = {"name": "Alice"}
        
        batch = Batch(data)
        batch.set("age", 30)
        result = batch.apply()
        
        assert result == {"name": "Alice", "age": 30}
        assert "age" not in data  # Original unchanged
    
    def test_batch_delete_operation(self):
        """Test basic delete operation in batch."""
        data = {"name": "Alice", "age": 30}
        
        batch = Batch(data)
        batch.delete("age")
        result = batch.apply()
        
        assert result == {"name": "Alice"}
        assert "age" in data  # Original unchanged
    
    def test_batch_update_operation(self):
        """Test basic update operation in batch."""
        data = {"user": {"name": "Alice"}}
        
        batch = Batch(data)
        batch.update("user", {"age": 30, "email": "alice@example.com"})
        result = batch.apply()
        
        assert result == {
            "user": {
                "name": "Alice",
                "age": 30,
                "email": "alice@example.com"
            }
        }
        assert "age" not in data["user"]  # Original unchanged
    
    def test_batch_append_operation(self):
        """Test basic append operation in batch."""
        data = {"items": [1, 2, 3]}
        
        batch = Batch(data)
        batch.append("items", 4)
        result = batch.apply()
        
        assert result == {"items": [1, 2, 3, 4]}
        assert len(data["items"]) == 3  # Original unchanged


class TestOperationClass:
    """Test the Operation dataclass."""
    
    def test_operation_creation(self):
        """Test creating Operation objects."""
        op = Operation(verb="set", path="a.b", value=42)
        assert op.verb == "set"
        assert op.path == "a.b"
        assert op.value == 42
    
    def test_operation_frozen(self):
        """Test that Operations are immutable."""
        op = Operation(verb="set", path="a.b", value=42)
        
        with pytest.raises(AttributeError):
            op.value = 100  # Can't modify frozen dataclass
    
    def test_operation_from_dict(self):
        """Test creating Operation from dictionary."""
        op_data = {"verb": "set", "path": "user.name", "value": "Alice"}
        op = Operation.from_dict(op_data)
        
        assert op.verb == "set"
        assert op.path == "user.name"
        assert op.value == "Alice"
    
    def test_operation_from_dict_delete(self):
        """Test creating delete Operation from dictionary."""
        op_data = {"verb": "delete", "path": "user.email"}
        op = Operation.from_dict(op_data)
        
        assert op.verb == "delete"
        assert op.path == "user.email"
        assert op.value is None
    
    def test_operation_from_dict_invalid_verb(self):
        """Test invalid verb raises error."""
        op_data = {"verb": "invalid", "path": "a.b", "value": 1}
        
        with pytest.raises(ValueError, match="Invalid operation verb"):
            Operation.from_dict(op_data)
    
    def test_operation_from_dict_missing_path(self):
        """Test missing path raises error."""
        op_data = {"verb": "set", "value": 1}
        
        with pytest.raises(ValueError, match="must contain a 'path' key"):
            Operation.from_dict(op_data)
    
    def test_operation_from_dict_missing_value(self):
        """Test missing value for non-delete raises error."""
        op_data = {"verb": "set", "path": "a.b"}
        
        with pytest.raises(ValueError, match="requires a 'value' key"):
            Operation.from_dict(op_data)
    
    def test_operation_from_dict_extra_keys(self):
        """Test extra keys are ignored."""
        op_data = {
            "verb": "set",
            "path": "a.b",
            "value": 42,
            "extra": "ignored",
            "another": "also ignored"
        }
        op = Operation.from_dict(op_data)
        
        assert op.verb == "set"
        assert op.path == "a.b"
        assert op.value == 42
        assert not hasattr(op, "extra")


class TestMultipleOperations:
    """Test batching multiple operations together."""
    
    def test_multiple_sets(self):
        """Test multiple set operations."""
        data = {"user": {}}
        
        batch = Batch(data)
        batch.set("user.name", "Alice")
        batch.set("user.age", 30)
        batch.set("user.email", "alice@example.com")
        result = batch.apply()
        
        assert result == {
            "user": {
                "name": "Alice",
                "age": 30,
                "email": "alice@example.com"
            }
        }
    
    def test_mixed_operations(self):
        """Test mixing different operation types."""
        data = {
            "user": {"name": "Alice", "age": 30, "temp": "remove"},
            "items": [1, 2],
            "metadata": {"version": 1}
        }
        
        batch = Batch(data)
        batch.set("user.verified", True)
        batch.delete("user.temp")
        batch.append("items", 3)
        batch.update("metadata", {"updated": "2024-01-01"})
        result = batch.apply()
        
        assert result == {
            "user": {"name": "Alice", "age": 30, "verified": True},
            "items": [1, 2, 3],
            "metadata": {"version": 1, "updated": "2024-01-01"}
        }
    
    def test_operation_order_matters(self):
        """Test that operations execute in order."""
        data = {"value": 10}
        
        # First set to 20, then to 30
        batch1 = Batch(data)
        batch1.set("value", 20)
        batch1.set("value", 30)
        result1 = batch1.apply()
        assert result1 == {"value": 30}
        
        # First set to 30, then to 20
        batch2 = Batch(data)
        batch2.set("value", 30)
        batch2.set("value", 20)
        result2 = batch2.apply()
        assert result2 == {"value": 20}
    
    def test_dependent_operations(self):
        """Test operations that depend on previous ones."""
        data = {}
        
        batch = Batch(data)
        # Create nested structure step by step
        batch.set("user", {})
        batch.set("user.profile", {})
        batch.set("user.profile.name", "Alice")
        batch.set("user.profile.settings", {})
        batch.update("user.profile.settings", {"theme": "dark"})
        
        result = batch.apply()
        assert result == {
            "user": {
                "profile": {
                    "name": "Alice",
                    "settings": {"theme": "dark"}
                }
            }
        }
    
    def test_delete_then_set(self):
        """Test deleting and then setting the same path."""
        data = {"user": {"old": "data", "keep": "this"}}
        
        batch = Batch(data)
        batch.delete("user.old")
        batch.set("user.new", "value")
        
        result = batch.apply()
        assert result == {
            "user": {
                "keep": "this",
                "new": "value"
            }
        }


class TestMethodChaining:
    """Test fluent method chaining."""
    
    def test_chain_operations(self):
        """Test chaining multiple operations."""
        data = {"base": "value"}
        
        result = (Batch(data)
            .set("name", "Alice")
            .set("age", 30)
            .delete("base")
            .set("items", [])
            .append("items", "first")
            .append("items", "second")
            .apply())
        
        assert result == {
            "name": "Alice",
            "age": 30,
            "items": ["first", "second"]
        }
    
    def test_complex_chain(self):
        """Test a complex chain of operations."""
        data = {
            "config": {"old": "remove"},
            "users": []
        }
        
        result = (Batch(data)
            .delete("config.old")
            .set("config.database.host", "localhost")
            .set("config.database.port", 5432)
            .append("users", {"name": "Alice", "role": "admin"})
            .append("users", {"name": "Bob", "role": "user"})
            .set("metadata.created", "2024-01-01")
            .update("metadata", {"version": "1.0"})
            .apply())
        
        assert result == {
            "config": {
                "database": {
                    "host": "localhost",
                    "port": 5432
                }
            },
            "users": [
                {"name": "Alice", "role": "admin"},
                {"name": "Bob", "role": "user"}
            ],
            "metadata": {
                "created": "2024-01-01",
                "version": "1.0"
            }
        }


class TestApplyFunction:
    """Test the declarative apply function."""
    
    def test_apply_basic(self):
        """Test basic apply with operation list."""
        data = {"name": "Alice"}
        
        operations = [
            {"verb": "set", "path": "age", "value": 30},
            {"verb": "set", "path": "email", "value": "alice@example.com"}
        ]
        
        result = apply(data, operations)
        assert result == {
            "name": "Alice",
            "age": 30,
            "email": "alice@example.com"
        }
    
    def test_apply_all_verbs(self):
        """Test apply with all verb types."""
        data = {
            "user": {"name": "Alice", "temp": "remove"},
            "items": [1, 2],
            "config": {"a": 1}
        }
        
        operations = [
            {"verb": "set", "path": "user.age", "value": 30},
            {"verb": "delete", "path": "user.temp"},
            {"verb": "append", "path": "items", "value": 3},
            {"verb": "update", "path": "config", "value": {"b": 2}}
        ]
        
        result = apply(data, operations)
        assert result == {
            "user": {"name": "Alice", "age": 30},
            "items": [1, 2, 3],
            "config": {"a": 1, "b": 2}
        }
    
    def test_apply_empty_operations(self):
        """Test apply with empty operation list."""
        data = {"a": 1}
        result = apply(data, [])
        
        assert result == {"a": 1}
        assert result is not data  # Still a copy
    
    def test_apply_nested_paths(self):
        """Test apply with deeply nested paths."""
        data = {}
        
        operations = [
            {"verb": "set", "path": "a.b.c.d.e", "value": "deep"},
            {"verb": "set", "path": "a.b.c.f", "value": "also deep"}
        ]
        
        result = apply(data, operations)
        assert result == {
            "a": {
                "b": {
                    "c": {
                        "d": {"e": "deep"},
                        "f": "also deep"
                    }
                }
            }
        }
    
    def test_apply_invalid_operation(self):
        """Test apply with invalid operation."""
        data = {"a": 1}
        
        operations = [
            {"verb": "invalid", "path": "a", "value": 2}
        ]
        
        with pytest.raises(ValueError, match="Invalid operation verb"):
            apply(data, operations)


class TestAtomicity:
    """Test atomic behavior of batch operations."""
    
    def test_all_or_nothing(self):
        """Test that operations are atomic - all succeed or none do."""
        data = {"user": {"name": "Alice"}}
        
        batch = Batch(data)
        batch.set("user.age", 30)
        batch.set("user.email", "alice@example.com")
        batch.update("user", {"verified": True})
        
        # All operations should be applied together
        result = batch.apply()
        
        # Check all operations were applied
        assert result["user"]["age"] == 30
        assert result["user"]["email"] == "alice@example.com"
        assert result["user"]["verified"] is True
        
        # Original should be completely unchanged
        assert data == {"user": {"name": "Alice"}}
    
    def test_immutability_preserved(self):
        """Test that batches preserve immutability."""
        data = {
            "level1": {
                "level2": {
                    "items": [1, 2, 3],
                    "value": 42
                }
            }
        }
        
        batch = Batch(data)
        batch.set("level1.level2.value", 100)
        batch.append("level1.level2.items", 4)
        batch.set("level1.new_key", "new_value")
        
        result = batch.apply()
        
        # Original completely unchanged
        assert data == {
            "level1": {
                "level2": {
                    "items": [1, 2, 3],
                    "value": 42
                }
            }
        }
        
        # Result has all modifications
        assert result["level1"]["level2"]["value"] == 100
        assert result["level1"]["level2"]["items"] == [1, 2, 3, 4]
        assert result["level1"]["new_key"] == "new_value"


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_batch_on_non_dict(self):
        """Test batch operations on non-dictionary data."""
        # List
        data = [1, 2, 3]
        batch = Batch(data)
        batch.append("", 4)  # Can't append to root list with empty path
        result = batch.apply()
        assert result == [1, 2, 3]  # No change
        
        # Set specific index
        batch = Batch([1, 2, 3])
        batch.set("1", 20)
        result = batch.apply()
        assert result == [1, 20, 3]
    
    def test_batch_with_none_values(self):
        """Test batch operations with None values."""
        data = {"value": None}
        
        batch = Batch(data)
        batch.set("value", "not none")
        batch.set("another", None)
        
        result = batch.apply()
        assert result == {"value": "not none", "another": None}
    
    def test_empty_path_operations(self):
        """Test operations with empty paths."""
        data = {"a": 1}
        
        batch = Batch(data)
        batch.set("", "root_value")
        
        result = batch.apply()
        assert result == {"a": 1, "": "root_value"}
    
    def test_operations_on_missing_paths(self):
        """Test operations on paths that don't exist."""
        data = {"a": 1}
        
        batch = Batch(data)
        batch.delete("missing.path")  # No effect
        batch.update("missing", {"key": "value"})  # No effect on non-dict
        batch.append("missing", "item")  # No effect on non-list
        
        result = batch.apply()
        assert result == {"a": 1}
    
    def test_large_batch(self):
        """Test a large batch of operations."""
        data = {"items": {}}
        
        batch = Batch(data)
        # Add 100 items
        for i in range(100):
            batch.set(f"items.item_{i}", i)
        
        result = batch.apply()
        assert len(result["items"]) == 100
        assert result["items"]["item_0"] == 0
        assert result["items"]["item_99"] == 99


class TestRealWorldScenarios:
    """Test real-world usage patterns."""
    
    def test_user_registration(self):
        """Test user registration workflow."""
        data = {"users": {}, "stats": {"total_users": 0}}
        
        # Register a new user atomically
        batch = Batch(data)
        batch.set("users.alice", {
            "email": "alice@example.com",
            "created": "2024-01-01",
            "profile": {}
        })
        batch.set("users.alice.profile.name", "Alice Smith")
        batch.set("users.alice.profile.avatar", "/default.png")
        batch.set("users.alice.settings", {"theme": "light", "notifications": True})
        batch.set("stats.total_users", 1)
        batch.set("stats.last_registration", "2024-01-01")
        
        result = batch.apply()
        
        assert "alice" in result["users"]
        assert result["users"]["alice"]["email"] == "alice@example.com"
        assert result["users"]["alice"]["profile"]["name"] == "Alice Smith"
        assert result["stats"]["total_users"] == 1
        
        # Original unchanged
        assert data["stats"]["total_users"] == 0
    
    def test_shopping_cart_update(self):
        """Test updating a shopping cart."""
        cart = {
            "user_id": 123,
            "items": [
                {"id": 1, "name": "Book", "quantity": 1, "price": 15.99}
            ],
            "total": 15.99,
            "discount": 0
        }
        
        # Add item, apply discount, update total - all atomic
        batch = Batch(cart)
        batch.append("items", {"id": 2, "name": "Pen", "quantity": 2, "price": 3.99})
        batch.set("discount", 5.00)
        batch.set("total", 19.98 - 5.00)
        batch.set("discount_code", "SAVE5")
        
        result = batch.apply()
        
        assert len(result["items"]) == 2
        assert result["total"] == 14.98
        assert result["discount"] == 5.00
        assert result["discount_code"] == "SAVE5"
        
        # Original cart unchanged
        assert len(cart["items"]) == 1
        assert cart["total"] == 15.99
    
    def test_configuration_migration(self):
        """Test migrating configuration format."""
        old_config = {
            "database": "postgres://localhost/mydb",
            "cache": "redis://localhost",
            "debug": "true",
            "port": "8080"
        }
        
        # Migrate to new structured format atomically
        operations = [
            # Create new structure
            {"verb": "set", "path": "db.connection_string", "value": "postgres://localhost/mydb"},
            {"verb": "set", "path": "db.type", "value": "postgresql"},
            {"verb": "set", "path": "cache.url", "value": "redis://localhost"},
            {"verb": "set", "path": "cache.enabled", "value": True},
            {"verb": "set", "path": "server.port", "value": 8080},
            {"verb": "set", "path": "server.debug", "value": True},
            {"verb": "set", "path": "version", "value": "2.0"},
            # Remove old keys
            {"verb": "delete", "path": "database"},
            {"verb": "delete", "path": "cache"},
            {"verb": "delete", "path": "debug"},
            {"verb": "delete", "path": "port"}
        ]
        
        new_config = apply(old_config, operations)
        
        assert "db" in new_config
        assert new_config["db"]["type"] == "postgresql"
        assert new_config["server"]["port"] == 8080
        assert new_config["version"] == "2.0"
        assert "database" not in new_config
        assert "port" not in new_config
    
    def test_form_submission(self):
        """Test processing form submission atomically."""
        form_state = {
            "fields": {
                "name": {"value": "", "error": None},
                "email": {"value": "", "error": None},
                "age": {"value": "", "error": None}
            },
            "submitted": False,
            "valid": False
        }
        
        # Process form submission
        batch = Batch(form_state)
        batch.set("fields.name.value", "Alice")
        batch.set("fields.email.value", "alice@example.com")
        batch.set("fields.age.value", "30")
        batch.set("submitted", True)
        batch.set("valid", True)
        batch.set("submission_time", "2024-01-01T10:00:00")
        
        result = batch.apply()
        
        assert result["fields"]["name"]["value"] == "Alice"
        assert result["submitted"] is True
        assert result["valid"] is True
        assert "submission_time" in result
        
        # Original form state unchanged
        assert form_state["submitted"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])