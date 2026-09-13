from collections.abc import AsyncGenerator
from contextlib import contextmanager
from typing import Any, Never, Optional, overload
from ..hdl import *
from ._base import BaseProcess, BaseEngine
from amaranth_types import ValueLike

__all__ = [
    "DomainReset",
    "BrokenTrigger",
    "SampleTrigger",
    "ChangedTrigger",
    "EdgeTrigger",
    "DelayTrigger",
    "TriggerCombination",
    "TickTrigger",
    "SimulatorContext",
    "ProcessContext",
    "TestbenchContext",
    "AsyncProcess",
]

class DomainReset(Exception):
    """Exception raised when the domain of a a tick trigger that is repeatedly awaited has its
    reset asserted."""

class BrokenTrigger(Exception):
    """Exception raised when a trigger that is repeatedly awaited in an `async for` loop has
    a matching event occur while the body of the `async for` loop is executing."""

class SampleTrigger:
    def __init__(self, value: ValueLike): ...

class ChangedTrigger:
    def __init__(self, signal: ValueLike): ...
    @property
    def value(self) -> Signal: ...

class EdgeTrigger:
    def __init__(self, signal: ValueLike, polarity: int): ...

class DelayTrigger:
    def __init__(self, interval: int | float): ...

class TriggerCombination:
    """
    TriggerCombination(...)

    A list of triggers, the activation of any of which will wake up the caller.

    A :class:`TriggerCombination` is an immutable object that stores a list of triggers and
    expressions to sample. The trigger combination wakes up the caller when any of these triggers
    activate, and it samples all of the signals at the same moment.

    The :meth:`SimulatorContext.delay`, :meth:`SimulatorContext.changed`, and
    :meth:`SimulatorContext.edge` methods create a trigger combination that consists of just that
    one trigger, while :meth:`TriggerCombination.delay`, :meth:`TriggerCombination.changed`, and
    :meth:`TriggerCombination.edge` methods create a trigger combination based on another trigger
    combination by extending it with an additional trigger. The :meth:`TriggerCombination.sample`
    method creates a trigger combination based on another trigger combination that wakes up
    the caller in the same conditions but additionally samples the specified expressions.

    To wait for a trigger combination to be activated once (a *one-shot* wait), a process or
    testbench calls :py:`await triggers`, usually on a newly created trigger combination: ::

        async def testbench(ctx):
            a_value, b_value = await ctx.changed(dut.a, dut.b)

    To repeatedly wait for a trigger combination to be activated (a *multi-shot* wait), a process
    or testbench :term:`asynchronously iterates <python:asynchronous iterable>` the trigger
    combination, usually using the :py:`async for` loop: ::

        async def testbench(ctx):
            async a_value, b_value in ctx.changed(dut.a, dut.b):
                ...

    Both one-shot and multi-shot waits return the same :class:`tuple` of return values, the elements
    of which are determined by the triggers and sampled expressions that have been added to
    the trigger combination, in the order in which they were added. For a detailed description of
    the return values, refer to :meth:`SimulatorContext.delay`, :meth:`SimulatorContext.changed`,
    :meth:`SimulatorContext.edge`, and :meth:`TriggerCombination.sample`.

    Aside from the syntax, there are two differences between one-shot and multi-shot waits:

    1. A multi-shot wait continues to observe the trigger combination while the process or testbench
       responds to the event. If the trigger combination is activated again before the next
       iteration of the asynchronous iterator (such as while the body of the :py:`async for` loop is
       executing), the next iteration raises a :exc:`BrokenTrigger` exception to notify the caller
       of the missed event.
    2. A repeated one-shot wait may be less efficient than a multi-shot wait.
    """
    def __init__(
        self,
        engine: BaseEngine,
        process: BaseProcess,
        *,
        triggers: tuple[DelayTrigger | ChangedTrigger | SampleTrigger | EdgeTrigger, ...] = ...,
    ): ...
    def sample(self, *values: ValueLike) -> TriggerCombination:
        r"""
        Sample signals when a trigger from this combination is activated.

        This method returns a new :class:`TriggerCombination` object. When awaited, this object
        returns, in addition to the values that would be returned by :py:`await trigger`, the values
        of :py:`exprs` at exactly the moment at which the wait has completed.

        Combining :meth:`~SimulatorContext.delay`, :meth:`~SimulatorContext.changed`, or
        :meth:`~SimulatorContext.edge` with :meth:`sample` can be used to capture the state of
        a circuit at the moment of the event: ::

            async for arst_edge, delay_expired, in_a_value, in_b_value in \
                    ctx.posedge(arst).delay(1e-3).sample(in_a, in_b):
                ...

        Chaining calls to :meth:`sample` has the same effect as calling it once with the combined
        list of arguments. The code below has the same behavior as the code above: ::

            async for arst_edge, delay_expired, in_a_value, in_b_value in \
                    ctx.posedge(arst).delay(1e-3).sample(in_a).sample(in_b):
                ...

        .. note::

            Chaining calls to this method is useful for defining reusable building blocks. See
            the documentation for :meth:`TickTrigger.sample` for a detailed example.
        """
        ...
    def changed(self, *signals: ValueLike) -> TriggerCombination:
        """
        Add a signal change trigger to the list of triggers.

        This method returns a new :class:`TriggerCombination` object. When awaited, this object
        also waits for the same trigger as :meth:`SimulatorContext.changed`, and returns,
        in addition to the values that would be returned by :py:`await trigger`, the values
        returned by :meth:`SimulatorContext.changed`.
        """
        ...
    def edge(self, signal: ValueLike, polarity: int) -> TriggerCombination:
        """
        Add a low-to-high or high-to-low transition trigger to the list of triggers.

        This method returns a new :class:`TriggerCombination` object. When awaited, this object
        also waits for the same trigger as :meth:`SimulatorContext.edge`, and returns,
        in addition to the values that would be returned by :py:`await trigger`, the values
        returned by :meth:`SimulatorContext.edge`.
        """
        ...
    def posedge(self, signal: ValueLike) -> TriggerCombination:
        """
        Add a low-to-high transition trigger to the list of triggers.

        Equivalent to :meth:`edge(signal, 1) <edge>`.
        """
        ...
    def negedge(self, signal: ValueLike) -> TriggerCombination:
        """
        Add a high-to-low transition trigger to the list of triggers.

        Equivalent to :meth:`edge(signal, 0) <edge>`.
        """
        ...
    def delay(self, interval: int | float) -> TriggerCombination:
        """
        Add a delay trigger to the list of triggers.

        This method returns a new :class:`TriggerCombination` object. When awaited, this object
        also waits for the same trigger as :meth:`SimulatorContext.delay`, and returns,
        in addition to the values that would be returned by :py:`await trigger`, the value
        returned by :meth:`SimulatorContext.delay`.
        """
        ...
    def __await__(self): ...
    async def __aiter__(self) -> AsyncGenerator: ...

class TickTrigger:
    """
    TickTrigger(...)

    A trigger that wakes up the caller when the active edge of a clock domain occurs or the domain
    is asynchronously reset.

    A :class:`TickTrigger` is an immutable object that stores a reference to a clock domain and
    a list of expressions to sample.

    The :meth:`SimulatorContext.tick` method creates a tick trigger with an empty list of sampled
    expressions, and the :meth:`TickTrigger.sample` method creates a tick trigger based on another
    tick trigger that additionally samples the specified expressions.

    To wait for a tick trigger to be activated once (a *one-shot* wait), a process or testbench
    calls :py:`await trigger`, usually on a newly created tick trigger: ::

        async def testbench(ctx):
            clk_hit, rst_active, a_value, b_value = await ctx.tick().sample(dut.a, dut.b)

    To repeatedly wait for a tick trigger to be activated (a *multi-shot* wait), a process or
    testbench :term:`asynchronously iterates <python:asynchronous iterable>` the tick trigger,
    usually using the :py:`async for` loop: ::

        async def testbench(ctx):
            async for clk_hit, rst_active, a_value, b_value in ctx.tick().sample(dut.a, dut.b):
                ...

    Both one-shot and multi-shot waits return the same :class:`tuple`
    :py:`(clk_hit, rst_active, *values)` of return values:

    1. :py:`clk_hit` is :py:`True` if there was an active clock edge at the moment the wait has
       completed, and :py:`False` otherwise (that is, if the clock domain was asynchronously reset).
    2. :py:`rst_active` is :py:`True` if the clock domain is reset (synchronously or asynchronously)
       at the moment the wait has completed, :py:`False` otherwise.
    3. All following return values correspond to the sampled expressions in the order in which they
       were added.

    Aside from the syntax, there are two differences between one-shot and multi-shot waits:

    1. A multi-shot wait continues to observe the tick trigger while the process or testbench
       responds to the event. If the tick trigger is activated again before the next iteration of
       the asynchronous iterator (such as while the body of the :py:`async for` loop is executing),
       the next iteration raises a :exc:`BrokenTrigger` exception to notify the caller of the missed
       event.
    2. A repeated one-shot wait may be less efficient than a multi-shot wait.

    .. note::

        The exact behavior of :py:`rst_active` differs depending on whether :py:`domain` uses
        synchronous or asynchronous reset; in both cases it is :py:`True` if and only if
        the domain reset has been asserted. Reusable processes and testbenches, as well as their
        building blocks, should handle both cases.
    """
    def __init__(
        self, engine: BaseEngine, process: BaseProcess, *, domain: ClockDomain, sampled: tuple[ValueLike] = ...
    ): ...
    def sample(self, *values: ValueLike) -> TickTrigger:
        r"""
        Sample expressions when this trigger is activated.

        This method returns a new :class:`TickTrigger` object. When awaited, this object returns,
        in addition to the values that would be otherwise returned by :py:`await trigger`,
        the values of :py:`exprs` (any :class:`~.hdl.ValueLike`) at exactly the moment at which
        the active clock edge, or the asynchronous reset (if applicable), has occurred.

        Combining :meth:`~SimulatorContext.tick` with :meth:`sample` can be used to capture
        the state of a circuit after the active clock edge, but before propagation of signal values
        that have been updated by that clock edge: ::

            async for clk_edge, rst_active, in_a_value, in_b_value in \
                    ctx.tick().sample(in_a, in_b):
                ...

        Chaining calls to :meth:`sample` has the same effect as calling it once with the combined
        list of arguments. The code below has the same behavior as the code above: ::

            async for clk_edge, rst_active, in_a_value, in_b_value in \
                    ctx.tick().sample(in_a).sample(in_b):
                ...

        .. note::

            Chaining calls to this method is useful for defining reusable building blocks.
            The following (simplified for clarity) implementation of :meth:`until` takes advantage
            of it by first appending :py:`condition` to the end of the list of captured expressions,
            checking if it holds, and then removing it from the list of sampled values: ::

                async def until(trigger, condition):
                    async for clk_edge, rst_active, *values, done in trigger.sample(condition):
                        if done:
                            return values
        """
        ...
    async def until(self, condition: ValueLike):
        r"""
        Repeat this trigger until a condition is met.

        This method awaits this trigger at least once, and returns a :class:`tuple` of the values
        that are :meth:`sample`\ d when :py:`condition` evaluates to a non-zero value. Values
        sampled during previous repeats are discarded.

        Awaiting a :py:`trigger` returns values indicating the state of the clock and reset signals,
        while awaiting :py:`trigger.until(...)` does not:

        .. code::

            while True:
                clk_edge, rst_active, *values, flag_value = await trigger.sample(flag) # never raises
                if flag_value:
                    break
            # `values` may be used after the loop finishes

        .. code::

            values = await trigger.until(flag) # may raise `DomainReset`

        Raises
        ------
        :exc:`TypeError`
            If the shape of :py:`condition` is a :class:`ShapeCastable`.
        :exc:`DomainReset`
            If the clock domain has been synchronously or asynchronously reset during the wait.
        """
        ...
    async def repeat(self, count: int):
        r"""
        Repeat this trigger a specific number of times.

        This method awaits this trigger at least once, and returns a :class:`tuple` of the values
        that are :meth:`sample`\ d during the last repeat. Values sampled during previous repeats
        are discarded.

        Awaiting a :py:`trigger` returns values indicating the state of the clock and reset signals,
        while awaiting :py:`trigger.repeat(...)` does not:

        .. code::

            for _ in range(3):
                clk_edge, rst_active, *values = await trigger # never raises
            # `values` may be used after the loop finishes

        .. code::

            values = await trigger.repeat(3) # may raise `DomainReset`

        Raises
        ------
        :exc:`ValueError`
            If :py:`count` is less than 1.
        :exc:`DomainReset`
            If the clock domain has been synchronously or asynchronously reset during the wait.
        """
        ...
    def __await__(self): ...
    async def __aiter__(self) -> AsyncGenerator: ...

class SimulatorContext:
    """
    SimulatorContext(...)

    Simulator context.

    Simulator processes and testbenches are :py:`async` Python functions that interact with
    the simulation using the only argument they receive: the *context*. Using a context, it is
    possible to sample or update signals and wait for events to occur in the simulation.

    The context has two kinds of methods: :py:`async` methods and non-:py:`async` methods. Calling
    an :py:`async` method may cause the caller to be preempted (be paused such that the simulation
    time can advance), while calling non-:py:`async` methods never causes that.

    .. note::

        While a testbench or process is executing without calling :py:`async` methods, no other
        testbench or process will run, with one exception: if a testbench calls :meth:`set`, all
        processes that wait (directly or indirectly) for the updated signals to change will execute
        before the call returns.
    """
    def __init__(self, design, engine: BaseEngine, process: BaseProcess): ...
    def delay(self, interval: int | float) -> TriggerCombination:
        """
        Wait until a time interval has elapsed.

        This method returns a :class:`TriggerCombination` object that, when awaited, pauses
        the execution of the calling process or testbench by :py:`interval` seconds. The returned
        object may be used to wait for multiple events.

        The value captured by this trigger is :py:`True` if the delay has expired when the wait has
        completed, and :py:`False` otherwise.

        The :py:`interval` may be zero, in which case the caller will be scheduled for execution
        immediately after all of the processes and testbenches scheduled for the current time step
        finish executing. In other words, if a call to :meth:`Simulator.advance` schedules a process
        or testbench and it performs :py:`await ctx.delay(0)`, this process or testbench will
        continue execution only during the next call to :meth:`Simulator.advance`.

        .. note::

            Although the behavior of :py:`await ctx.delay(0)` is well-defined, it may make waveforms
            difficult to understand and simulations hard to reason about.

        Raises
        ------
        :exc:`ValueError`
            If :py:`delay` is negative.
        """
        ...
    def changed(self, *signals: ValueLike) -> TriggerCombination:
        """
        Asynchronously wait until one of the signals change.

        This method returns a :class:`TriggerCombination` object that, when awaited, pauses
        the execution of the calling process or testbench until any of the :py:`signals` change.
        The returned object may be used to wait for multiple events.

        The values captured by this trigger are the values of :py:`signals` at the time the wait
        has completed.

        .. warning::

            The simulation may produce *glitches*: transient changes to signals (e.g. from 0 to 1
            and back to 0) during combinational propagation that are invisible in testbenches or
            waveform captures. Glitches will wake up **both processes and testbenches** that use
            this method to wait for a signal to change, and both processes and testbenches must be
            prepared to handle such spurious wakeups. The presence, count, and sequence in which
            glitches occur may also vary between simulation runs.

            Testbenches that wait for a signal to change using an :py:`await` statement might only
            observe the final value of the signal, and testbenches that wait for changes using
            an :py:`async for` loop will crash with a :exc:`BrokenTrigger` exception if they
            encounter a glitch.

            Processes will observe all of the transient values of the signal.
        """
        ...
    def edge(self, signal: ValueLike, polarity: int) -> TriggerCombination:
        """
        Asynchronously wait until a low-to-high or high-to-low transition of a signal occurs.

        This method returns a :class:`TriggerCombination` object that, when awaited, pauses
        the execution of the calling process or testbench until the value of :py:`signal`
        (a single-bit signal or a single-bit slice of a signal) changes from :py:`not polarity`
        to :py:`polarity`. The returned object may be used to wait for multiple events.

        The value captured by this trigger is :py:`True` if the relevant transition has occurred
        at the time the wait has completed, and :py:`False` otherwise.

        .. warning::

            In most cases, this method should not be used to wait for a status signal to be asserted
            or deasserted in a testbench because it is likely to introduce a race condition.
            Whenever a suitable clock domain is available, use
            :py:`await ctx.tick().until(signal == polarity)` instead.

        Raises
        ------
        :exc:`TypeError`
            If :py:`signal` is neither a single-bit :class:`Signal` nor a single-bit slice of
            a :class:`Signal`.
        :exc:`TypeError`
            If the shape of :py:`signal` is a :class:`ShapeCastable`.
        :exc:`ValueError`
            If :py:`polarity` is neither 0 nor 1.
        """
        ...
    def posedge(self, signal: ValueLike) -> TriggerCombination:
        """
        Asynchronously wait until a signal is asserted.

        Equivalent to :meth:`edge(signal, 1) <edge>`.
        """
        ...
    @overload
    def tick(self, domain: str = ..., *, context: Optional[Elaboratable] = ...) -> TickTrigger:
        """
        Wait until an active clock edge or an asynchronous reset occurs.

        This method returns a :class:`TickTrigger` object that, when awaited, pauses the execution
        of the calling process or testbench until the active edge of the clock, or the asynchronous
        reset (if applicable), occurs. The returned object may be used to repeatedly wait for one
        of these events until a condition is satisfied or a specific number of times. See
        the :ref:`tick trigger reference <sim-tick-trigger>` for more details.

        The :py:`domain` may be either a :class:`ClockDomain` or a :class:`str`. If it is
        a :class:`str`, a clock domain with this name is looked up in
        the :ref:`elaboratable <lang-elaboration>` :py:`context`, or in :py:`toplevel` if
        :py:`context` is not provided.

        Raises
        ------
        :exc:`ValueError`
            If :py:`domain` is :py:`"comb"`.
        :exc:`ValueError`
            If :py:`domain` is a :class:`~.hdl.ClockDomain` and :py:`context` is provided and not
            :py:`None`.
        :exc:`ValueError`
            If :py:`context` is an elaboratable that is not a direct or indirect submodule of
            :py:`toplevel`.
        :exc:`NameError`
            If :py:`domain` is a :class:`str`, but there is no clock domain with this name in
            :py:`context` or :py:`toplevel`.
        """
        ...
    @overload
    def tick(self, domain: ClockDomain) -> TickTrigger:
        """
        Wait until an active clock edge or an asynchronous reset occurs.

        This method returns a :class:`TickTrigger` object that, when awaited, pauses the execution
        of the calling process or testbench until the active edge of the clock, or the asynchronous
        reset (if applicable), occurs. The returned object may be used to repeatedly wait for one
        of these events until a condition is satisfied or a specific number of times. See
        the :ref:`tick trigger reference <sim-tick-trigger>` for more details.

        The :py:`domain` may be either a :class:`ClockDomain` or a :class:`str`. If it is
        a :class:`str`, a clock domain with this name is looked up in
        the :ref:`elaboratable <lang-elaboration>` :py:`context`, or in :py:`toplevel` if
        :py:`context` is not provided.

        Raises
        ------
        :exc:`ValueError`
            If :py:`domain` is :py:`"comb"`.
        :exc:`ValueError`
            If :py:`domain` is a :class:`~.hdl.ClockDomain` and :py:`context` is provided and not
            :py:`None`.
        :exc:`ValueError`
            If :py:`context` is an elaboratable that is not a direct or indirect submodule of
            :py:`toplevel`.
        :exc:`NameError`
            If :py:`domain` is a :class:`str`, but there is no clock domain with this name in
            :py:`context` or :py:`toplevel`.
        """
        ...
    def tick(self, domain: str | ClockDomain = ..., *, context: Optional[Elaboratable] = ...) -> TickTrigger:
        """
        Wait until an active clock edge or an asynchronous reset occurs.

        This method returns a :class:`TickTrigger` object that, when awaited, pauses the execution
        of the calling process or testbench until the active edge of the clock, or the asynchronous
        reset (if applicable), occurs. The returned object may be used to repeatedly wait for one
        of these events until a condition is satisfied or a specific number of times. See
        the :ref:`tick trigger reference <sim-tick-trigger>` for more details.

        The :py:`domain` may be either a :class:`ClockDomain` or a :class:`str`. If it is
        a :class:`str`, a clock domain with this name is looked up in
        the :ref:`elaboratable <lang-elaboration>` :py:`context`, or in :py:`toplevel` if
        :py:`context` is not provided.

        Raises
        ------
        :exc:`ValueError`
            If :py:`domain` is :py:`"comb"`.
        :exc:`ValueError`
            If :py:`domain` is a :class:`~.hdl.ClockDomain` and :py:`context` is provided and not
            :py:`None`.
        :exc:`ValueError`
            If :py:`context` is an elaboratable that is not a direct or indirect submodule of
            :py:`toplevel`.
        :exc:`NameError`
            If :py:`domain` is a :class:`str`, but there is no clock domain with this name in
            :py:`context` or :py:`toplevel`.
        """
        ...
    @contextmanager
    def critical(self):
        """
        Context manager that temporarily makes the caller critical.

        Testbenches and processes may be *background* or *critical*, where critical ones prevent
        :meth:`Simulator.run` from finishing. Processes are always created background, while
        testbenches are created critical by default, but may also be created background.
        This context manager makes the caller critical for the span of the :py:`with` statement.

        This may be useful in cases where an operation (for example, a bus transaction) takes
        multiple clock cycles to complete, and must be completed after starting, but the testbench
        or process performing it never finishes, always waiting for the next operation to arrive.
        In this case, the caller would elevate itself to become critical only for the duration of
        the operation itself using this context manager, for example: ::

            async def testbench_bus_transaction(ctx):
                # On every cycle, check whether the bus has an active transaction...
                async for clk_edge, rst_active, bus_active_value in ctx.tick().sample(bus.active):
                    if bus_active_value: # ... if it does...
                        with ctx.critical(): # ... make this testbench critical...
                            addr_value = ctx.get(bus.r_addr)
                            ctx.set(bus.r_data, ...) # ... perform the access...
                            await ctx.tick()
                            ctx.set(bus.done, 1)
                            await ctx.tick()
                            ctx.set(bus.done, 0) # ... and complete the transaction later.
                        # The `run()` method could return at this point, but not before.
        """
        ...
    @overload
    def get(self, expr: Value) -> int:
        """
        Sample the value of an expression.

        The behavior of this method depends on the type of :py:`expr`:

        - If it is a :class:`~.hdl.ValueCastable` whose shape is a :class:`~.hdl.ShapeCastable`,
          its numeric value is converted to a higher-level representation using
          :meth:`~.hdl.ShapeCastable.from_bits` and then returned.
        - If it is a :class:`~.hdl.Value` or a :class:`~.hdl.ValueCastable` whose shape is
          a :class:`~.hdl.Shape`, the numeric value is returned as an :class:`int`.

        This method is only available in testbenches.

        Raises
        ------
        :exc:`TypeError`
            If the caller is a process.
        """
        ...
    @overload
    def get(self, expr: ValueCastable) -> Any:
        """
        Sample the value of an expression.

        The behavior of this method depends on the type of :py:`expr`:

        - If it is a :class:`~.hdl.ValueCastable` whose shape is a :class:`~.hdl.ShapeCastable`,
          its numeric value is converted to a higher-level representation using
          :meth:`~.hdl.ShapeCastable.from_bits` and then returned.
        - If it is a :class:`~.hdl.Value` or a :class:`~.hdl.ValueCastable` whose shape is
          a :class:`~.hdl.Shape`, the numeric value is returned as an :class:`int`.

        This method is only available in testbenches.

        Raises
        ------
        :exc:`TypeError`
            If the caller is a process.
        """
        ...
    def get(self, expr: Value | ValueCastable) -> Any:
        """
        Sample the value of an expression.

        The behavior of this method depends on the type of :py:`expr`:

        - If it is a :class:`~.hdl.ValueCastable` whose shape is a :class:`~.hdl.ShapeCastable`,
          its numeric value is converted to a higher-level representation using
          :meth:`~.hdl.ShapeCastable.from_bits` and then returned.
        - If it is a :class:`~.hdl.Value` or a :class:`~.hdl.ValueCastable` whose shape is
          a :class:`~.hdl.Shape`, the numeric value is returned as an :class:`int`.

        This method is only available in testbenches.

        Raises
        ------
        :exc:`TypeError`
            If the caller is a process.
        """
        ...
    @overload
    def set(self, expr: Value, value: int) -> None:
        """
        Update the value of an expression.

        The behavior of this method depends on the type of :py:`expr`:

        - If it is a :class:`~.hdl.ValueCastable` whose shape is a :class:`~.hdl.ShapeCastable`,
          :py:`value` is converted to a numeric representation using
          :meth:`~.hdl.ShapeCastable.const` and then assigned.
        - If it is a :class:`~.hdl.Value` or a :class:`~.hdl.ValueCastable` whose shape is
          a :class:`~.hdl.Shape`, :py:`value` is assigned as-is.

        This method is available in both processes and testbenches.

        When used in a testbench, this method runs all processes that wait (directly or
        indirectly) for the signals in :py:`expr` to change, and returns only after the change
        propagates through the simulated circuits.
        """
        ...
    @overload
    def set(self, expr: ValueCastable, value: Any) -> None:
        """
        Update the value of an expression.

        The behavior of this method depends on the type of :py:`expr`:

        - If it is a :class:`~.hdl.ValueCastable` whose shape is a :class:`~.hdl.ShapeCastable`,
          :py:`value` is converted to a numeric representation using
          :meth:`~.hdl.ShapeCastable.const` and then assigned.
        - If it is a :class:`~.hdl.Value` or a :class:`~.hdl.ValueCastable` whose shape is
          a :class:`~.hdl.Shape`, :py:`value` is assigned as-is.

        This method is available in both processes and testbenches.

        When used in a testbench, this method runs all processes that wait (directly or
        indirectly) for the signals in :py:`expr` to change, and returns only after the change
        propagates through the simulated circuits.
        """
        ...
    def set(self, expr: Value | ValueCastable, value: Any) -> None:
        """
        Update the value of an expression.

        The behavior of this method depends on the type of :py:`expr`:

        - If it is a :class:`~.hdl.ValueCastable` whose shape is a :class:`~.hdl.ShapeCastable`,
          :py:`value` is converted to a numeric representation using
          :meth:`~.hdl.ShapeCastable.const` and then assigned.
        - If it is a :class:`~.hdl.Value` or a :class:`~.hdl.ValueCastable` whose shape is
          a :class:`~.hdl.Shape`, :py:`value` is assigned as-is.

        This method is available in both processes and testbenches.

        When used in a testbench, this method runs all processes that wait (directly or
        indirectly) for the signals in :py:`expr` to change, and returns only after the change
        propagates through the simulated circuits.
        """
        ...

class ProcessContext(SimulatorContext):
    def get(self, expr: ValueLike) -> Never: ...
    @overload
    def set(self, expr: Value, value: int) -> None: ...
    @overload
    def set(self, expr: ValueCastable, value: Any) -> None: ...
    def set(self, expr: Value | ValueCastable, value: Any) -> None: ...

class TestbenchContext(SimulatorContext):
    @overload
    def get(self, expr: Value) -> int: ...
    @overload
    def get(self, expr: ValueCastable) -> Any: ...
    def get(self, expr: Value | ValueCastable) -> Any: ...
    @overload
    def set(self, expr: Value, value: int) -> None: ...
    @overload
    def set(self, expr: ValueCastable, value: Any) -> None: ...
    def set(self, expr: Value | ValueCastable, value: Any) -> None: ...

class AsyncProcess(BaseProcess):
    def __init__(self, design, engine: BaseEngine, constructor, *, testbench: bool, background): ...
    def reset(self) -> None: ...
    def run(self) -> None: ...
