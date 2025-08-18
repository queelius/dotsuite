from typing import Any, List, Dict, Literal, Union
from dataclasses import dataclass, fields
from copy import deepcopy

# dotbatch's core purpose is to orchestrate dotmod. It is a critical dependency.
from shape.dotmod.core import set_, delete_, update_, append_


# Define the universe of possible modification verbs.
OpVerb = Literal["set", "delete", "update", "append"]

# A declarative, JSON-friendly representation of an operation.
OpData = Dict[str, Union[str, Any]]


@dataclass(frozen=True)
class Operation:
    """A pure data representation of a single modification operation."""
    verb: OpVerb
    path: str
    value: Any = None  # `value` is optional for 'delete'

    @classmethod
    def from_dict(cls, data: OpData) -> 'Operation':
        """Creates an Operation from a dictionary, ensuring validity."""
        verb = data.get("verb")
        if verb not in ("set", "delete", "update", "append"):
            raise ValueError(f"Invalid operation verb: {verb}")
        
        if "path" not in data:
            raise ValueError("Operation dictionary must contain a 'path' key.")

        if verb != "delete" and "value" not in data:
             raise ValueError(f"Verb '{verb}' requires a 'value' key.")

        valid_keys = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        
        return cls(**filtered_data)


class Batch:
    """
    Builds and executes a transaction of multiple modification operations.
    This ensures atomicity: all operations succeed or none do, preventing
    intermediate, inconsistent states.
    """
    def __init__(self, initial_data: Any):
        # We don't copy here; the final apply() will do it once.
        self._initial_data = initial_data
        self.ops: List[Operation] = []

    def set(self, path: str, value: Any) -> 'Batch':
        self.ops.append(Operation(verb="set", path=path, value=value))
        return self

    def delete(self, path: str) -> 'Batch':
        self.ops.append(Operation(verb="delete", path=path))
        return self

    def update(self, path: str, value: Dict) -> 'Batch':
        self.ops.append(Operation(verb="update", path=path, value=value))
        return self

    def append(self, path: str, value: Any) -> 'Batch':
        self.ops.append(Operation(verb="append", path=path, value=value))
        return self

    def apply(self) -> Any:
        """
        Applies all staged operations in a single atomic unit.
        Returns a new object with all modifications applied.
        """
        mod_functions = {
            "set": set_, "delete": delete_,
            "update": update_, "append": append_
        }
        
        # Start with a deep copy to ensure the original object is never mutated.
        current_data = deepcopy(self._initial_data)
        
        for op in self.ops:
            func = mod_functions[op.verb]
            
            if op.verb == "delete":
                current_data = func(current_data, op.path)
            else:
                current_data = func(current_data, op.path, op.value)
                
        return current_data


def apply(data: Any, operations: List[OpData]) -> Any:
    """
    A convenience function to apply a declarative list of operations
    to a data structure in a single transaction.

    Args:
        data: The initial data structure to modify.
        operations: A list of dictionaries, each representing one operation.
                    e.g., [{"verb": "set", "path": "a.b", "value": 1}]
    
    Returns:
        A new data structure with all modifications applied.
    """
    batch = Batch(data)
    batch.ops = [Operation.from_dict(op_data) for op_data in operations]
    return batch.apply()
