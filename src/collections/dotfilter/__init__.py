from .core import (
    QuerySet,
    filter_docs,
    filter_by_path,
    filter_by_existence,
    combine_filters
)

__all__ = [
    "QuerySet",
    "filter_docs", 
    "filter_by_path",
    "filter_by_existence",
    "combine_filters"
]
__version__ = "0.1.0"