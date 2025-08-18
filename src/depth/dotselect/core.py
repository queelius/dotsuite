
# We alias the functions from the master `dotpath` engine.
# `dotselect` is just a curated, user-friendly interface to the powerful
# engine that underpins the entire addressing pillar.
from dotpath import find_all, find_first

__all__ = ['find_all', 'find_first']
