"""
This type stub file was generated by pyright.
"""

__all__ = ["flatten", "union", "memoize", "final", "deprecated", "get_linter_options", "get_linter_option"]

def flatten(i): # -> Generator[str | Unknown, Unknown, None]:
    ...

def union(i, start=...): # -> None:
    ...

def memoize(f): # -> _Wrapped[..., Unknown, (*args: Unknown), Unknown]:
    ...

def final(cls):
    ...

def deprecated(message, stacklevel=...): # -> (f: Unknown) -> _Wrapped[..., Unknown, (*args: Unknown, **kwargs: Unknown), Unknown]:
    ...

def extend(cls): # -> (f: Unknown) -> None:
    ...

def get_linter_options(filename): # -> dict[str, str] | dict[Unknown, Unknown]:
    ...

def get_linter_option(filename, name, type, default): # -> int | bool:
    ...
