from typing import Any, Callable, Dict, Iterable, Union
import operator
import re

from depth.dotpath import create_default_engine


# --- DSL Exceptions ---

class DSLError(ValueError):
    """Base exception for DSL parsing errors."""
    pass


class DSLSyntaxError(DSLError):
    """Raised when DSL syntax is invalid."""
    pass


class UnknownOperatorError(DSLError):
    """Raised when an unknown operator is encountered."""
    pass


class MissingValueError(DSLError):
    """Raised when an operator requires a value but none is provided."""
    pass


def _re_match_op(v, r):
    """Internal helper for regex matching."""
    return bool(re.match(r, str(v)))


# --- Core Query and Expression Classes (AST) ---

class Query:
    """
    Represents a query that can be evaluated against a data object.
    The core building block for creating compositional, reusable queries.
    
    Can be initialized with either:
    - An Expression object (AST node)
    - A string in the DSL format (e.g., "status equals active")
    """

    def __init__(self, expression: Union["Expression", str]):
        if isinstance(expression, str):
            self.expression = parse_dsl(expression)
        else:
            self.expression = expression

    def evaluate(self, data: Any) -> bool:
        """
        Evaluates the query expression against the given data object.

        Args:
            data: The dict or list to evaluate against.

        Returns:
            True if the query matches, False otherwise.
        """
        return self.expression.evaluate(data)

    def __and__(self, other: "Query") -> "Query":
        """Combines this query with another using a logical AND."""
        return Query(And(self.expression, other.expression))

    def __or__(self, other: "Query") -> "Query":
        """Combines this query with another using a logical OR."""
        return Query(Or(self.expression, other.expression))

    def __invert__(self) -> "Query":
        """Negates this query."""
        return Query(Not(self.expression))

    def __call__(self, data: Any) -> bool:
        """Allows the query to be called like a function."""
        return self.evaluate(data)

    def filter(self, data: Iterable[Any]) -> Iterable[Any]:
        """Filters an iterable of data objects, yielding matches."""
        return (item for item in data if self.evaluate(item))


class Expression:
    """Base class for all query expressions (AST nodes)."""

    def evaluate(self, data: Any) -> bool:
        """Evaluates the expression against a data object."""
        raise NotImplementedError

    def __and__(self, other: "Expression") -> "And":
        """Creates an AND expression."""
        return And(self, other)

    def __or__(self, other: "Expression") -> "Or":
        """Creates an OR expression."""
        return Or(self, other)

    def __invert__(self) -> "Not":
        """Creates a NOT expression."""
        return Not(self)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the expression to a dictionary."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expression":
        """Deserializes a dictionary into an Expression object."""
        node_type = data.pop("type")
        if node_type == "and":
            return And.from_dict(data)
        elif node_type == "or":
            return Or.from_dict(data)
        elif node_type == "not":
            return Not.from_dict(data)
        elif node_type == "condition":
            return Condition.from_dict(data)
        else:
            raise ValueError(f"Unknown expression type: {node_type}")


class And(Expression):
    """Represents a logical AND operation between two expressions."""

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def evaluate(self, data: Any) -> bool:
        """Evaluates both sides and returns True if both are True."""
        return self.left.evaluate(data) and self.right.evaluate(data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "and",
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "And":
        left = Expression.from_dict(data["left"])
        right = Expression.from_dict(data["right"])
        return cls(left, right)


class Or(Expression):
    """Represents a logical OR operation between two expressions."""

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def evaluate(self, data: Any) -> bool:
        """Evaluates both sides and returns True if either is True."""
        return self.left.evaluate(data) or self.right.evaluate(data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "or",
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Or":
        left = Expression.from_dict(data["left"])
        right = Expression.from_dict(data["right"])
        return cls(left, right)


class Not(Expression):
    """Represents a logical NOT operation on an expression."""

    def __init__(self, expression: Expression):
        self.expression = expression

    def evaluate(self, data: Any) -> bool:
        """Returns the negated result of the inner expression."""
        return not self.expression.evaluate(data)

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "not", "expression": self.expression.to_dict()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Not":
        expression = Expression.from_dict(data["expression"])
        return cls(expression)


class Condition(Expression):
    """
    Represents a leaf condition in the query AST.
    It checks if a value extracted via a dotpath satisfies a given operator.
    """

    def __init__(
        self,
        path: str,
        op: Callable[[Any, Any], bool],
        value: Any,
        quantifier: Callable[[Iterable], bool] = any,
    ):
        self.path = path
        self.op = op
        self.value = value
        self.quantifier = quantifier

    def evaluate(self, data: Any) -> bool:
        """
        Evaluates the condition.
        The result depends on the quantifier (`any` or `all`).
        If no values are found at the path, the condition is False (unless using all() on empty).
        """
        try:
            # First try to use dotpath engine
            engine = create_default_engine()
            
            # Handle paths that might be shortcuts (e.g., "users.active" -> "users.*.active")
            path = self.path
            
            # Check if path looks like it's trying to access a field in array elements
            # e.g., "users.active" when users is an array
            parts = path.split('.')
            if len(parts) >= 2:
                # Get the parent path to check if it's an array
                parent_path = '.'.join(parts[:-1])
                try:
                    parent_ast = engine.parse(parent_path)
                    parent_values = list(engine.evaluate(parent_ast, data))
                    if parent_values and isinstance(parent_values[0], list):
                        # Parent is a list, so add wildcard
                        path = parent_path + '.*.' + parts[-1]
                except:
                    pass  # Keep original path
            
            # Try to parse and evaluate the path
            try:
                ast = engine.parse(path)
                values = list(engine.evaluate(ast, data))
            except ValueError:
                # Path parsing failed, try manual traversal for numeric indices
                values = self._manual_path_traversal(data, self.path)
            
            # Handle empty results
            if not values:
                # Special case: all() on empty collection is True (vacuous truth)
                if self.quantifier == all:
                    return True
                return False
            
            # Special handling: if path points to a single list/collection,
            # apply the operator to each element
            if len(values) == 1 and isinstance(values[0], (list, tuple)):
                collection = values[0]
                if not collection:
                    # Empty collection
                    if self.quantifier == all:
                        return True  # Vacuous truth
                    return False
                return self.quantifier(self.op(item, self.value) for item in collection)
            
            # Normal case: apply operator to each value found
            return self.quantifier(self.op(v, self.value) for v in values)
        except Exception:
            # If path traversal fails, treat as not found
            # But still respect vacuous truth for all()
            if self.quantifier == all:
                return True
            return False
    
    def _manual_path_traversal(self, data: Any, path: str) -> list:
        """Manual path traversal for paths with numeric indices."""
        parts = path.split('.')
        current = data
        
        try:
            for part in parts:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, (list, tuple)):
                    if part.isdigit():
                        current = current[int(part)]
                    else:
                        # Trying to access field on list items
                        return [item.get(part) if isinstance(item, dict) else None 
                                for item in current]
                else:
                    return []
            return [current]
        except (KeyError, IndexError, TypeError, AttributeError):
            return []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "condition",
            "path": self.path,
            "op": self.op.__name__,
            "value": self.value,
            "quantifier": self.quantifier.__name__,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Condition":
        OP_MAP = {
            "eq": operator.eq,
            "ne": operator.ne,
            "gt": operator.gt,
            "ge": operator.ge,
            "lt": operator.lt,
            "le": operator.le,
            "contains": operator.contains,
            "matches": _re_match_op,
        }
        QUANTIFIER_MAP = {"any": any, "all": all}

        op_name = data["op"]
        op_func = OP_MAP.get(op_name)
        if op_func is None:
            raise ValueError(f"Unknown operator function: {op_name}")

        quantifier_name = data.get("quantifier", "any") # Default to 'any'
        quantifier_func = QUANTIFIER_MAP.get(quantifier_name)
        if quantifier_func is None:
            raise ValueError(f"Unknown quantifier function: {quantifier_name}")

        return cls(
            path=data["path"],
            op=op_func,
            value=data["value"],
            quantifier=quantifier_func,
        )


# --- Fluent Query Builder ---

class Q:
    """
    A factory for creating Query objects in a fluent, Pythonic way.

    Provides a more intuitive and readable way to construct complex queries
    by chaining methods, for example:
    `Q("user.profile.tags").contains("python")`
    `Q("items.price").all().greater(10)`
    """

    def __init__(self, path: str, quantifier: Callable[[Iterable], bool] = any):
        self.path = path
        self.quantifier = quantifier

    def all(self) -> "Q":
        """
        Applies the 'all' quantifier to the next condition.
        This requires that *all* values found at the path satisfy the condition.
        If no values are found, it evaluates to True.
        """
        return Q(self.path, quantifier=all)

    def equals(self, value: Any) -> Query:
        """Checks if the value at path is equal to the given value."""
        return Query(Condition(self.path, operator.eq, value, self.quantifier))

    def not_equals(self, value: Any) -> Query:
        """Checks if the value at path is not equal to the given value."""
        return Query(Condition(self.path, operator.ne, value, self.quantifier))

    def greater(self, value: Any) -> Query:
        """Checks if the value at path is greater than the given value."""
        return Query(Condition(self.path, operator.gt, value, self.quantifier))

    def greater_equal(self, value: Any) -> Query:
        """Checks if the value at path is greater than or equal to the given value."""
        return Query(Condition(self.path, operator.ge, value, self.quantifier))

    def less(self, value: Any) -> Query:
        """Checks if the value at path is less than the given value."""
        return Query(Condition(self.path, operator.lt, value, self.quantifier))

    def less_equal(self, value: Any) -> Query:
        """Checks if the value at path is less than or equal to the given value."""
        return Query(Condition(self.path, operator.le, value, self.quantifier))

    def contains(self, value: Any) -> Query:
        """Checks if the collection at path contains the given value."""
        return Query(Condition(self.path, operator.contains, value, self.quantifier))

    def matches(self, regex: str) -> Query:
        """Checks if the string value at path matches the given regex."""
        return Query(Condition(self.path, _re_match_op, regex, self.quantifier))


# --- DSL Parser ---

def parse_dsl(dsl: str) -> Expression:
    """
    Parses a human-friendly DSL string into an Expression AST.
    
    Supported formats:
    - "path equals value" - Check equality
    - "path greater 10" - Comparison operators
    - "path contains item" - Check containment
    - "path matches regex" - Regex matching
    - "any path equals value" - Explicit any quantifier
    - "all path equals value" - All quantifier
    - "not path equals value" - Negation
    - "(path equals value) and (path2 greater 10)" - Logical operations
    
    Examples:
        "status equals active"
        "age greater 25"
        "tags contains python"
        "all users.active equals true"
        "(status equals active) and (age greater 25)"
        "not deleted equals true"
    """
    # Remove extra whitespace
    dsl = ' '.join(dsl.split())
    
    # Handle negation FIRST (before checking for and/or)
    # This allows "not (expression and expression)" to work
    if dsl.startswith('not '):
        inner = dsl[4:].strip()
        # Parse the inner expression, which might have its own structure
        return Not(parse_dsl(inner))
    elif dsl.startswith('not('):
        # Handle case with no space: not(expression)
        inner = dsl[3:].strip()
        # Parse the inner expression, which might have its own structure
        return Not(parse_dsl(inner))
    
    # Handle parenthesized expressions for and/or
    if ' and ' in dsl or ' or ' in dsl:
        return _parse_logical_expression(dsl)
    
    # Remove outer parentheses if present
    dsl = dsl.strip()
    if dsl.startswith('(') and dsl.endswith(')'):
        # Make sure these are the outermost parens
        depth = 0
        for i, char in enumerate(dsl):
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0 and i < len(dsl) - 1:
                    # Closing paren before end, don't strip
                    break
        else:
            # Outer parens enclose everything
            dsl = dsl[1:-1].strip()
    
    # Parse single condition
    return _parse_condition(dsl)


def _parse_logical_expression(dsl: str) -> Expression:
    """Parse expressions with and/or operators."""
    # Find the rightmost top-level operator (for left-associativity)
    depth = 0
    last_and = -1
    last_or = -1
    
    for i, char in enumerate(dsl):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif depth == 0:
            # Check for operators at top level
            if dsl[i:i+5] == ' and ':
                last_and = i
            elif dsl[i:i+4] == ' or ':
                last_or = i
    
    # Process OR first (lower precedence)
    if last_or >= 0:
        left = dsl[:last_or].strip()
        right = dsl[last_or+4:].strip()
        return Or(parse_dsl(left), parse_dsl(right))
    
    # Then process AND
    if last_and >= 0:
        left = dsl[:last_and].strip()
        right = dsl[last_and+5:].strip()
        return And(parse_dsl(left), parse_dsl(right))
    
    # No top-level operator found
    # Remove outer parentheses if they enclose the whole expression
    dsl = dsl.strip()
    if dsl.startswith('(') and dsl.endswith(')'):
        # Check if these parens enclose the whole expression
        depth = 0
        for i, char in enumerate(dsl):
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0 and i < len(dsl) - 1:
                    # Closing paren before the end, don't strip
                    break
        else:
            # The outer parens enclose everything
            # Re-parse without the outer parens to check for operators inside
            inner = dsl[1:-1].strip()
            return parse_dsl(inner)
    
    return _parse_condition(dsl)


def _parse_condition(dsl: str) -> Condition:
    """Parse a single condition."""
    dsl = dsl.strip()
    
    # Check for quantifier prefix
    quantifier = any
    if dsl.startswith('any '):
        quantifier = any
        dsl = dsl[4:]
    elif dsl.startswith('all '):
        quantifier = all
        dsl = dsl[4:]
    
    # Parse path and operator
    # We need to be careful with quoted values
    parts = []
    current_part = []
    in_quotes = False
    quote_char = None
    
    for i, char in enumerate(dsl):
        if not in_quotes:
            if char in ('"', "'"):
                in_quotes = True
                quote_char = char
                current_part.append(char)
            elif char == ' ' and len(parts) < 2:
                # Space outside quotes, and we haven't found operator yet
                if current_part:
                    parts.append(''.join(current_part))
                    current_part = []
            else:
                current_part.append(char)
        else:
            current_part.append(char)
            if char == quote_char and (i == 0 or dsl[i-1] != '\\'):
                in_quotes = False
                quote_char = None
    
    # Add the last part
    if current_part:
        parts.append(''.join(current_part))
    
    if len(parts) < 2:
        # Check if this is an exists check
        if len(parts) == 1 and ' ' not in dsl:
            # Just a path, no operator - not valid
            raise DSLSyntaxError(f"Missing operator in DSL expression: {dsl}")
        raise DSLSyntaxError(f"Invalid DSL syntax: {dsl}")
    
    path = parts[0]
    op_str = parts[1].lower()
    
    # Parse the value (if present)
    value = None
    if len(parts) > 2:
        value_str = parts[2]
        
        # Check if value is quoted
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            # Remove quotes and handle escaped quotes
            value = value_str[1:-1].replace('\\"', '"').replace("\\'", "'")
        elif value_str.lower() == 'true':
            value = True
        elif value_str.lower() == 'false':
            value = False
        elif value_str.lower() == 'null' or value_str.lower() == 'none':
            value = None
        else:
            # Try to parse as number
            try:
                if '.' in value_str:
                    value = float(value_str)
                else:
                    value = int(value_str)
            except ValueError:
                # Keep as string
                value = value_str
    elif op_str not in ('exists',):
        # Most operators need a value
        raise MissingValueError(f"Operator '{op_str}' requires a value")
    
    # Map operator strings to functions
    op_map = {
        'equals': operator.eq,
        'eq': operator.eq,
        '=': operator.eq,
        '==': operator.eq,
        'not_equals': operator.ne,
        'ne': operator.ne,
        '!=': operator.ne,
        'greater': operator.gt,
        'gt': operator.gt,
        '>': operator.gt,
        'greater_equal': operator.ge,
        'ge': operator.ge,
        '>=': operator.ge,
        'less': operator.lt,
        'lt': operator.lt,
        '<': operator.lt,
        'less_equal': operator.le,
        'le': operator.le,
        '<=': operator.le,
        'contains': operator.contains,
        'in': operator.contains,
        'matches': _re_match_op,
        'regex': _re_match_op,
    }
    
    op_func = op_map.get(op_str)
    if op_func is None:
        # Check for 'exists' special case
        if op_str == 'exists':
            # "path exists" means the path has a truthy value
            return Condition(path, lambda v, _: bool(v), True, quantifier)
        raise UnknownOperatorError(f"Unknown operator: {op_str}")
    
    return Condition(path, op_func, value, quantifier)
