import functools
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Union

# dotpipe has a critical dependency on the dotpath engine to resolve paths.
try:
    from dotpath import find_all
except ImportError:
    # If dotpath is not installed, raise a helpful error.
    raise ImportError("dotpipe requires the 'dotpath' library. Please install it.")


# --- Safe Function Registry for the DSL ---

def _flatten_list(list_of_lists: List[List[Any]]) -> List[Any]:
    """Helper to flatten a list of lists into a single list."""
    if not isinstance(list_of_lists, list):
        return list_of_lists # Return as-is if not a list
    return [item for sublist in list_of_lists if isinstance(sublist, list) for item in sublist]

def _unique_items(items: List[Any]) -> List[Any]:
    """Helper to get unique items from a list, preserving order for predictability."""
    try:
        return list(dict.fromkeys(items))
    except TypeError:
        # Fallback for unhashable items like dictionaries
        return items

# This registry defines the "standard library" of safe, named functions
# that the declarative DSL can reference by string.
SAFE_FUNCTIONS: Dict[str, Callable] = {
    "len": len,
    "sum": sum,
    "upper": str.upper,
    "lower": str.lower,
    "flatten": _flatten_list,
    "unique": _unique_items,
    "first": lambda x: x[0] if x else None,
    "last": lambda x: x[-1] if x else None,
}


class Pipeline:
    """
    Builds and executes a transformation pipeline on a single dictionary.

    This class provides a fluent, chainable interface for defining a series
    of transformation steps. The pipeline is immutable; it never alters the
    original source data.
    """

    def __init__(self, data: Dict[str, Any]):
        if not isinstance(data, dict):
            raise TypeError("Pipeline can only be initialized with a dictionary.")
        # Store the original data for path lookups and a mutable state for transformation.
        # A deepcopy ensures complete isolation from the original user-provided object.
        self._source_data = deepcopy(data)
        self._current_state = deepcopy(data)

    def assign(self, new_field: str, *, from_path: str, then: Optional[Union[str, List[str], Callable]] = None) -> 'Pipeline':
        """
        Adds a new field to the result, calculated from a path on the source data.

        Args:
            new_field: The name of the new field to create.
            from_path: A dotquery path string to select data from the original source document.
            then: An optional function or list of named functions to apply to the selected data.
        """
        # find_all always returns an iterable.
        selected_values = list(find_all(self._source_data, from_path))

        # If a path resolves to a single item, we process that item directly.
        # If it resolves to multiple, we process the list.
        # If nothing is found, the value is None.
        if len(selected_values) == 1:
            value_to_process = selected_values[0]
        else:
            value_to_process = selected_values if selected_values else None

        final_value = _apply_function_chain(value_to_process, then)
        self._current_state[new_field] = final_value
        return self

    def pluck(self, *fields: str) -> 'Pipeline':
        """
        Selects only the specified fields from the current result, discarding all others.
        """
        self._current_state = {field: self._current_state[field] for field in fields if field in self._current_state}
        return self

    def delete(self, *fields: str) -> 'Pipeline':
        """
        Removes the specified fields from the current result.
        """
        for field in fields:
            self._current_state.pop(field, None)
        return self

    def apply_to(self, field: str, func: Union[str, List[str], Callable]) -> 'Pipeline':
        """
        Applies a function or function chain to an existing field in the current result.
        """
        if field in self._current_state:
            self._current_state[field] = _apply_function_chain(self._current_state[field], func)
        return self

    def apply(self) -> Dict[str, Any]:
        """
        Finalizes the pipeline and returns the resulting transformed dictionary.
        """
        return self._current_state


def from_dsl(data: Dict[str, Any], pipeline_dsl: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Executes a transformation pipeline defined by a declarative, serializable DSL.

    Args:
        data: The source dictionary to transform.
        pipeline_dsl: A list of step objects, where each object defines a verb and its arguments.
    
    Returns:
        The final, transformed dictionary.
    """
    pipeline = Pipeline(data)

    for step in pipeline_dsl:
        verb = step.get("verb")
        if not verb:
            raise ValueError("Each step in the DSL must have a 'verb' key.")

        if verb == "assign":
            pipeline.assign(step["field"], from_path=step["path"], then=step.get("then"))
        elif verb == "pluck":
            pipeline.pluck(*step.get("fields", []))
        elif verb == "delete":
            pipeline.delete(*step.get("fields", []))
        elif verb == "apply_to":
            pipeline.apply_to(step["field"], func=step["func"])
        else:
            raise ValueError(f"Unknown verb in dotpipe DSL: {verb}")

    return pipeline.apply()


def _apply_function_chain(value: Any, funcs: Optional[Union[str, List[str], Callable]]) -> Any:
    """Internal helper to resolve and apply a function or a chain of functions."""
    if funcs is None:
        return value

    if not isinstance(funcs, list):
        funcs = [funcs]

    result = value
    for func_item in funcs:
        if callable(func_item):
            # If it's already a Python callable, just use it.
            resolved_func = func_item
        elif isinstance(func_item, str):
            # If it's a string, look it up in the safe registry.
            resolved_func = SAFE_FUNCTIONS.get(func_item)
            if not resolved_func:
                raise ValueError(f"Unknown or unsafe function in 'then' clause: {func_item}")
        else:
            raise TypeError(f"Function must be a callable or a registered function name (str), not {type(func_item)}")
        
        result = resolved_func(result)
        
    return result
