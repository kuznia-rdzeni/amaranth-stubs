"""
This type stub file was generated by pyright.
"""

from .._utils import deprecated
from ..hdl._cd import *
from ..hdl._ir import *

__all__ = ["Settle", "Delay", "Tick", "Passive", "Active"]
class Command:
    ...


class Settle(Command):
    def __repr__(self) -> str:
        ...
    


class Delay(Command):
    def __init__(self, interval=...) -> None:
        ...
    
    def __repr__(self) -> str:
        ...
    


class Tick(Command):
    domain: str | ClockDomain

    def __init__(self, domain: str | ClockDomain = ...) -> None:
        ...
    
    def __repr__(self) -> str:
        ...
    

class Passive(Command):
    def __repr__(self) -> str:
        ...
    


class Active(Command):
    def __repr__(self) -> str:
        ...
    


