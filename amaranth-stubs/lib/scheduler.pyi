from .. import *
from amaranth_types import HasElaborate

class RoundRobin(Elaboratable):
    count: int
    requests: Signal
    grant: Signal
    valid: Signal
    def __init__(self, *, count: int):
        ...

    def elaborate(self, platform) -> HasElaborate:
        ...
