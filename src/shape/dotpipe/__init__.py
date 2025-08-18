from .core import Pipeline, from_dsl

# Create a pipe function for consistency with other modules
pipe = from_dsl

__all__ = ["Pipeline", "from_dsl", "pipe"]
__version__ = "0.1.0"