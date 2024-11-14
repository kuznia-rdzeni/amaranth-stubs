from collections.abc import AsyncGenerator
from contextlib import contextmanager
from typing import Any, Never, Optional, overload
from ..hdl import *
from ._base import BaseProcess, BaseEngine
from amaranth_types import ValueLike


__all__ = [
    "DomainReset", "BrokenTrigger",
    "SampleTrigger", "ChangedTrigger", "EdgeTrigger", "DelayTrigger",
    "TriggerCombination", "TickTrigger",
    "SimulatorContext", "ProcessContext", "TestbenchContext", "AsyncProcess",
]


class DomainReset(Exception):
    """Exception raised when the domain of a a tick trigger that is repeatedly awaited has its
    reset asserted."""


class BrokenTrigger(Exception):
    """Exception raised when a trigger that is repeatedly awaited in an `async for` loop has
    a matching event occur while the body of the `async for` loop is executing."""


class SampleTrigger:
    def __init__(self, value: ValueLike):
        ...


class ChangedTrigger:
    def __init__(self, signal: ValueLike):
        ...

    @property
    def value(self) -> Signal:
        ...


class EdgeTrigger:
    def __init__(self, signal: ValueLike, polarity: int):
        ...


class DelayTrigger:
    def __init__(self, interval: int | float):
        ...


class TriggerCombination:
    def __init__(self, engine: BaseEngine, process: BaseProcess, *,
            triggers: tuple[DelayTrigger|ChangedTrigger|SampleTrigger|EdgeTrigger, ...] = ...):
        ...

    def sample(self, *values: ValueLike) -> TriggerCombination:
        ...

    def changed(self, *signals: ValueLike) -> TriggerCombination:
        ...

    def edge(self, signal: ValueLike, polarity: int) -> TriggerCombination:
        ...

    def posedge(self, signal: ValueLike) -> TriggerCombination:
        ...

    def negedge(self, signal: ValueLike) -> TriggerCombination:
        ...

    def delay(self, interval: int | float) -> TriggerCombination:
        ...

    def __await__(self):
        ...

    async def __aiter__(self) -> AsyncGenerator:
        ...


class TickTrigger:
    def __init__(self, engine: BaseEngine, process: BaseProcess, *,
            domain: ClockDomain, sampled: tuple[ValueLike] = ...):
        ...

    def sample(self, *values: ValueLike) -> TickTrigger:
        ...

    async def until(self, condition: ValueLike):
        ...

    async def repeat(self, count: int):
        ...

    def __await__(self):
        ...

    async def __aiter__(self) -> AsyncGenerator:
        ...


class SimulatorContext:
    def __init__(self, design, engine: BaseEngine, process: BaseProcess):
        ...

    def delay(self, interval: int | float) -> TriggerCombination:
        ...

    def changed(self, *signals: ValueLike) -> TriggerCombination:
        ...

    def edge(self, signal: ValueLike, polarity: int) -> TriggerCombination:
        ...

    def posedge(self, signal: ValueLike) -> TriggerCombination:
        ...

    @overload
    def tick(self, domain: str = ..., *, context: Optional[Elaboratable] = ...) -> TickTrigger: ...

    @overload
    def tick(self, domain: ClockDomain) -> TickTrigger: ...

    def tick(self, domain: str | ClockDomain = ..., *, context: Optional[Elaboratable] = ...) -> TickTrigger:
        ...

    @contextmanager
    def critical(self):
        ...
    
    @overload
    def get(self, expr: Value) -> int: ...

    @overload
    def get(self, expr: ValueCastable) -> Any: ...

    def get(self, expr: Value | ValueCastable) -> Any:
        ...

    @overload
    def set(self, expr: Value, value: int) -> None: ...

    @overload
    def set(self, expr: ValueCastable, value: Any) -> None: ...

    def set(self, expr: Value | ValueCastable, value: Any) -> None:
        ...


class ProcessContext(SimulatorContext):
    def get(self, expr: ValueLike) -> Never:
        ...

    @overload
    def set(self, expr: Value, value: int) -> None: ...

    @overload
    def set(self, expr: ValueCastable, value: Any) -> None: ...

    def set(self, expr: Value | ValueCastable, value: Any) -> None:
        ...


class TestbenchContext(SimulatorContext):
    @overload
    def get(self, expr: Value) -> int: ...

    @overload
    def get(self, expr: ValueCastable) -> Any: ...

    def get(self, expr: Value | ValueCastable) -> Any:
        ...

    @overload
    def set(self, expr: Value, value: int) -> None: ...

    @overload
    def set(self, expr: ValueCastable, value: Any) -> None: ...

    def set(self, expr: Value | ValueCastable, value: Any) -> None:
        ...


class AsyncProcess(BaseProcess):
    def __init__(self, design, engine: BaseEngine, constructor, *, testbench: bool, background):
        ...

    def reset(self) -> None:
        ...

    def run(self) -> None:
        ...
