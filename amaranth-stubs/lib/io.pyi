import enum
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from typing import Optional

from amaranth_types.types import IOValueLike

from ..hdl import *
from ..lib import wiring


__all__ = [
    "Direction", "PortLike", "SingleEndedPort", "DifferentialPort", "SimulationPort",
    "Buffer", "FFBuffer", "DDRBuffer",
    "Pin",
]


class Direction(enum.Enum):
    """Represents a direction of an I/O port, or of an I/O buffer."""

    #: Input direction (from world to Amaranth design)
    Input  = "i"
    #: Output direction (from Amaranth design to world)
    Output = "o"
    #: Bidirectional (can be switched between input and output)
    Bidir  = "io"

    def __or__(self, other: Direction) -> Direction:
        ...

    def __and__(self, other: Direction) -> Direction:
        ...


class PortLike(metaclass=ABCMeta):
    """Represents an abstract port that can be passed to a buffer.

    The port types supported by most platforms are :class:`SingleEndedPort` and
    :class:`DifferentialPort`. Platforms may define additional custom port types as appropriate.
    """

    @property
    @abstractmethod
    def direction(self) -> Direction:
        """The direction of this port, as :class:`Direction`."""
        ...

    @abstractmethod
    def __len__(self) -> int:
        """Returns the width of this port in bits."""
        ...

    @abstractmethod
    def __getitem__(self, index: int | slice) -> PortLike:
        """Slices the port, returning another :class:`PortLike` with a subset
        of its bits.

        The index can be a :class:`slice` or :class:`int`. If the index is
        an :class:`int`, the result is a single-bit :class:`PortLike`."""
        ...

    @abstractmethod
    def __invert__(self) -> PortLike:
        """Returns a new :class:`PortLike` object like this one, but with inverted polarity.

        The result should be such that using :class:`Buffer` on it is equivalent to using
        :class:`Buffer` on the original, with added inverters on the :py:`i` and :py:`o` ports."""
        ...

    @abstractmethod
    def __add__(self, other) -> PortLike:
        """Concatenates two library I/O ports of the same type.
        The direction of the resulting port is:
        * The same as the direction of both, if the two ports have the same direction.
        * :attr:`Direction.Input` if a bidirectional port is concatenated with an input port.
        * :attr:`Direction.Output` if a bidirectional port is concatenated with an output port.
        Returns
        -------
        :py:`type(self)`
            A new :py:`type(self)` which contains wires from :py:`self` followed by wires
            from :py:`other`, preserving their polarity inversion.
        Raises
        ------
        :exc:`ValueError`
            If an input port is concatenated with an output port.
        :exc:`TypeError`
            If :py:`self` and :py:`other` have different types.
        """
        ...


class SingleEndedPort(PortLike):
    """Represents a single-ended I/O port with optional inversion.

    Parameters
    ----------
    io : :class:`IOValue`
        The raw I/O value being wrapped.
    invert : :class:`bool` or iterable of :class:`bool`
        If true, the electrical state of the physical pin will be opposite from the Amaranth value
        (the ``*Buffer`` classes will insert inverters on :py:`o` and :py:`i` pins, as appropriate).

        This can be used for various purposes:

        - Normalizing active-low pins (such as ``CS_B``) to be active-high in Amaranth code
        - Compensating for boards where an inverting level-shifter (or similar circuitry) was used
          on the pin

        If the value is a simple :class:`bool`, it is used for all bits of this port. If the value
        is an iterable of :class:`bool`, the iterable must have the same length as :py:`io`, and
        the inversion is specified per-bit.
    direction : :class:`Direction` or :class:`str`
        Represents the allowed directions of this port. If equal to :attr:`Direction.Input` or
        :attr:`Direction.Output`, this port can only be used with buffers of matching direction.
        If equal to :attr:`Direction.Bidir`, this port can be used with buffers of any direction.
        If a string is passed, it is cast to :class:`Direction`.
    """
    def __init__(self, io: IOValueLike, *, invert : bool | Iterable[bool] = ..., direction: str | Direction = ...) -> None:
        ...

    @property
    def io(self) -> IOValue:
        """The :py:`io` argument passed to the constructor."""
        ...

    @property
    def invert(self) -> tuple[bool, ...]:
        """The :py:`invert` argument passed to the constructor, normalized to a :class:`tuple`
        of :class:`bool`."""
        ...

    @property
    def direction(self) -> Direction:
        """The :py:`direction` argument passed to the constructor, normalized to :class:`Direction`."""
        ...

    def __len__(self) -> int:
        """Returns the width of this port in bits. Equal to :py:`len(self.io)`."""
        ...

    def __invert__(self) -> SingleEndedPort:
        """Returns a new :class:`SingleEndedPort` with the opposite value of :py:`invert`."""
        ...

    def __getitem__(self, index: int | slice) -> SingleEndedPort:
        """Slices the port, returning another :class:`SingleEndedPort` with a subset
        of its bits.

        The index can be a :class:`slice` or :class:`int`. If the index is
        an :class:`int`, the result is a single-bit :class:`SingleEndedPort`."""
        ...

    def __add__(self, other: SingleEndedPort) -> SingleEndedPort:
        ...

    def __repr__(self) -> str:
        ...


class DifferentialPort(PortLike):
    """Represents a differential I/O port with optional inversion.

    Parameters
    ----------
    p : :class:`IOValue`
        The raw I/O value used as positive (true) half of the port.
    n : :class:`IOValue`
        The raw I/O value used as negative (complemented) half of the port. Must have the same
        length as :py:`p`.
    invert : :class:`bool` or iterable of :class`bool`
        If true, the electrical state of the physical pin will be opposite from the Amaranth value
        (the ``*Buffer`` classes will insert inverters on :py:`o` and :py:`i` pins, as appropriate).

        This can be used for various purposes:

        - Normalizing active-low pins (such as ``CS_B``) to be active-high in Amaranth code
        - Compensating for boards where the P and N pins are swapped (e.g. for easier routing)

        If the value is a simple :class:`bool`, it is used for all bits of this port. If the value
        is an iterable of :class:`bool`, the iterable must have the same length as :py:`io`, and
        the inversion is specified per-bit.
    direction : :class:`Direction` or :class:`str`
        Represents the allowed directions of this port. If equal to :attr:`Direction.Input` or
        :attr:`Direction.Output`, this port can only be used with buffers of matching direction.
        If equal to :attr:`Direction.Bidir`, this port can be used with buffers of any direction.
        If a string is passed, it is cast to :class:`Direction`.
    """
    def __init__(self, p: IOValueLike, n: IOValueLike, *, invert: bool | Iterable[bool] = ..., direction : str | Direction = ...) -> None:
        ...

    @property
    def p(self) -> IOValue:
        """The :py:`p` argument passed to the constructor."""
        ...

    @property
    def n(self) -> IOValue:
        """The :py:`n` argument passed to the constructor."""
        ...

    @property
    def invert(self) -> tuple[bool, ...]:
        """The :py:`invert` argument passed to the constructor, normalized to a :class:`tuple`
        of :class:`bool`."""
        ...

    @property
    def direction(self) -> Direction:
        """The :py:`direction` argument passed to the constructor, normalized to :class:`Direction`."""
        ...

    def __len__(self) -> int:
        """Returns the width of this port in bits. Equal to :py:`len(self.p)` (and :py:`len(self.n)`)."""
        ...

    def __invert__(self) -> DifferentialPort:
        """Returns a new :class:`DifferentialPort` with the opposite value of :py:`invert`."""
        ...

    def __getitem__(self, index: int | slice) -> DifferentialPort:
        """Slices the port, returning another :class:`DifferentialPort` with a subset
        of its bits.

        The index can be a :class:`slice` or :class:`int`. If the index is
        an :class:`int`, the result is a single-bit :class:`DifferentialPort`."""
        ...

    def __add__(self, other: DifferentialPort) -> DifferentialPort:
        ...

    def __repr__(self) -> str:
        ...


class SimulationPort(PortLike):
    """Represents a simulation library I/O port.
    Implements the :class:`PortLike` interface.
    Parameters
    ----------
    direction : :class:`Direction` or :class:`str`
        Set of allowed buffer directions. A string is converted to a :class:`Direction` first.
        If equal to :attr:`~Direction.Input` or :attr:`~Direction.Output`, this port can only be
        used with buffers of matching direction. If equal to :attr:`~Direction.Bidir`, this port
        can be used with buffers of any direction.
    width : :class:`int`
        Width of the port. The width of each of the attributes :py:`i`, :py:`o`, :py:`oe` (whenever
        present) equals :py:`width`.
    invert : :class:`bool` or iterable of :class:`bool`
        Polarity inversion. If the value is a simple :class:`bool`, it specifies inversion for
        the entire port. If the value is an iterable of :class:`bool`, the iterable must have the
        same length as the width of :py:`p` and :py:`n`, and the inversion is specified for
        individual wires.
    name : :class:`str` or :py:`None`
        Name of the port. This name is only used to derive the names of the input, output, and
        output enable signals.
    src_loc_at : :class:`int`
        :ref:`Source location <lang-srcloc>`. Used to infer :py:`name` if not specified.
    Attributes
    ----------
    i : :class:`Signal`
        Input signal. Present if :py:`direction in (Input, Bidir)`.
    o : :class:`Signal`
        Ouptut signal. Present if :py:`direction in (Output, Bidir)`.
    oe : :class:`Signal`
        Output enable signal. Present if :py:`direction in (Output, Bidir)`.
    invert : :class:`tuple` of :class:`bool`
        The :py:`invert` parameter, normalized to specify polarity inversion per-wire.
    direction : :class:`Direction`
        The :py:`direction` parameter, normalized to the :class:`Direction` enumeration.
    """
    def __init__(self, direction: str | Direction, width: int, *, invert: bool | Iterable[bool] = ..., name: Optional[str] = ..., src_loc_at: int = ...) -> None:
        ...

    @property
    def i(self) -> Signal:
        ...

    @property
    def o(self) -> Signal:
        ...

    @property
    def oe(self) -> Signal:
        ...

    @property
    def invert(self) -> tuple[bool, ...]:
        ...

    @property
    def direction(self) -> Direction:
        ...

    def __len__(self) -> int:
        ...

    def __getitem__(self, key: int | slice) -> SimulationPort:
        ...

    def __invert__(self) -> SimulationPort:
        ...

    def __add__(self, other) -> SimulationPort:
        ...

    def __repr__(self) -> str:
        ...


class Buffer(wiring.Component):
    """A combinatorial I/O buffer.

    Parameters
    ----------
    direction : :class:`Direction`
    port : :class:`PortLike`

    Attributes
    ----------
    signature : :class:`Buffer.Signature`
        Created based on constructor arguments.
    """
    class Signature(wiring.Signature):
        """A signature of a combinatorial I/O buffer.

        Parameters
        ----------
        direction : :class:`Direction`
        width : :class:`int`

        Attributes
        ----------
        i: :py:`unsigned(width)` (if :py:`direction in (Direction.Input, Direction.Bidir)`)
        o: :py:`unsigned(width)` (if :py:`direction in (Direction.Output, Direction.Bidir)`)
        oe: :py:`unsigned(1, init=0)` (if :py:`direction is Direction.Bidir`)
        oe: :py:`unsigned(1, init=1)` (if :py:`direction is Direction.Output`)
        """
        def __init__(self, direction: Direction, width: int) -> None:
            ...

        @property
        def direction(self) -> Direction:
            ...

        @property
        def width(self) -> int:
            ...

        def __eq__(self, other) -> bool:
            ...

        def __repr__(self) -> str:
            ...

    @property
    def signature(self) -> Signature:
        ...

    def __init__(self, direction: Direction, port: PortLike) -> None:
        ...

    @property
    def port(self) -> PortLike:
        ...

    @property
    def direction(self) -> Direction:
        ...

    def elaborate(self, platform) -> Module:
        ...


class FFBuffer(wiring.Component):
    """A registered I/O buffer.

    Equivalent to a plain :class:`Buffer` combined with reset-less registers on :py:`i`, :py:`o`,
    :py:`oe`.

    Parameters
    ----------
    direction : :class:`Direction`
    port : :class:`PortLike`
    i_domain : :class:`str`
        Domain for input register. Only used when :py:`direction in (Direction.Input, Direction.Bidir)`.
        Defaults to :py:`"sync"`
    o_domain : :class:`str`
        Domain for output and output enable registers. Only used when
        :py:`direction in (Direction.Output, Direction.Bidir)`. Defaults to :py:`"sync"`

    Attributes
    ----------
    signature : FFBuffer.Signature
        Created based on constructor arguments.
    """
    class Signature(wiring.Signature):
        """A signature of a registered I/O buffer.

        Parameters
        ----------
        direction : :class:`Direction`
        width : :class:`int`

        Attributes
        ----------
        i: :py:`unsigned(width)` (if :py:`direction in (Direction.Input, Direction.Bidir)`)
        o: :py:`unsigned(width)` (if :py:`direction in (Direction.Output, Direction.Bidir)`)
        oe: :py:`unsigned(1, init=0)` (if :py:`direction is Direction.Bidir`)
        oe: :py:`unsigned(1, init=1)` (if :py:`direction is Direction.Output`)
        """
        def __init__(self, direction: Direction, width: int) -> None:
            ...

        @property
        def direction(self) -> Direction:
            ...

        @property
        def width(self) -> int:
            ...

        def __eq__(self, other) -> bool:
            ...

        def __repr__(self) -> str:
            ...

    @property
    def signature(self) -> Signature:
        ...

    def __init__(self, direction: Direction, port: PortLike, *, i_domain: Optional[str] = ..., o_domain: Optional[str] = ...) -> None:
        if not isinstance(port, PortLike):
            raise TypeError(f"'port' must be a 'PortLike', not {port!r}")
        self._port = port
        super().__init__(FFBuffer.Signature(direction, len(port)).flip())
        if self.signature.direction is not Direction.Output:
            self._i_domain = i_domain or "sync"
        elif i_domain is not None:
            raise ValueError("Output buffer doesn't have an input domain")
        if self.signature.direction is not Direction.Input:
            self._o_domain = o_domain or "sync"
        elif o_domain is not None:
            raise ValueError("Input buffer doesn't have an output domain")
        if port.direction is Direction.Input and self.direction is not Direction.Input:
            raise ValueError(f"Input port cannot be used with {self.direction.name} buffer")
        if port.direction is Direction.Output and self.direction is not Direction.Output:
            raise ValueError(f"Output port cannot be used with {self.direction.name} buffer")

    @property
    def port(self) -> PortLike:
        ...

    @property
    def direction(self) -> Direction:
        ...

    @property
    def i_domain(self) -> str:
        ...

    @property
    def o_domain(self) -> str:
        ...

    def elaborate(self, platform) -> Module:
        ...


class DDRBuffer(wiring.Component):
    """A double data rate registered I/O buffer.

    In the input direction, the port is sampled at both edges of the input clock domain.
    The data sampled on the active clock edge of the domain appears on :py:`i[0]` with a delay
    of 1 clock cycle. The data sampled on the opposite clock edge appears on :py:`i[1]` with a delay
    of 0.5 clock cycle. Both :py:`i[0]` and :py:`i[1]` thus change on the active clock edge of the domain.

    In the output direction, both :py:`o[0]` and :py:`o[1]` are sampled on the active clock edge
    of the domain.  The value of :py:`o[0]` immediately appears on the output port.  The value
    of :py:`o[1]` then appears on the output port on the opposite edge, with a delay of 0.5 clock cycle.

    Support for this compoment is platform-specific, and may be missing on some platforms.

    Parameters
    ----------
    direction : :class:`Direction`
    port : :class:`PortLike`
    i_domain : :class:`str`
        Domain for input register. Only used when :py:`direction in (Direction.Input, Direction.Bidir)`.
    o_domain : :class:`str`
        Domain for output and output enable registers. Only used when
        :py:`direction in (Direction.Output, Direction.Bidir)`.

    Attributes
    ----------
    signature : DDRBuffer.Signature
        Created based on constructor arguments.
    """
    class Signature(wiring.Signature):
        """A signature of a double data rate registered I/O buffer.

        Parameters
        ----------
        direction : :class:`Direction`
        width : :class:`int`

        Attributes
        ----------
        i: :py:`unsigned(ArrayLayout(width, 2))` (if :py:`direction in (Direction.Input, Direction.Bidir)`)
        o: :py:`unsigned(ArrayLayout(width, 2))` (if :py:`direction in (Direction.Output, Direction.Bidir)`)
        oe: :py:`unsigned(1, init=0)` (if :py:`direction is Direction.Bidir`)
        oe: :py:`unsigned(1, init=1)` (if :py:`direction is Direction.Output`)
        """
        def __init__(self, direction: Direction, width: int) -> None:
            ...

        @property
        def direction(self) -> Direction:
            ...

        @property
        def width(self) -> int:
            ...

        def __eq__(self, other) -> bool:
            ...

        def __repr__(self) -> str:
            ...

    @property
    def signature(self) -> Signature:
        ...

    def __init__(self, direction: Direction, port: PortLike, *, i_domain: Optional[str] = ..., o_domain: Optional[str] = ...) -> None:
        ...

    @property
    def port(self) -> PortLike:
        ...

    @property
    def direction(self) -> Direction:
        ...

    @property
    def i_domain(self) -> str:
        ...

    @property
    def o_domain(self) -> str:
        ...

    def elaborate(self, platform):
        ...


class Pin(wiring.PureInterface):
    """
    An interface to an I/O buffer or a group of them that provides uniform access to input, output,
    or tristate buffers that may include a 1:n gearbox. (A 1:2 gearbox is typically called "DDR".)

    This is an interface object using :class:`Pin.Signature` as its signature.  The signature flows
    are defined from the point of view of a component that drives the I/O buffer.

    Parameters
    ----------
    width : int
        Width of the ``i``/``iN`` and ``o``/``oN`` signals.
    dir : ``"i"``, ``"o"``, ``"io"``, ``"oe"``
        Direction of the buffers. If ``"i"`` is specified, only the ``i``/``iN`` signals are
        present. If ``"o"`` is specified, only the ``o``/``oN`` signals are present. If ``"oe"`` is
        specified, the ``o``/``oN`` signals are present, and an ``oe`` signal is present.
        If ``"io"`` is specified, both the ``i``/``iN`` and ``o``/``oN`` signals are present, and
        an ``oe`` signal is present.
    xdr : int
        Gearbox ratio. If equal to 0, the I/O buffer is combinatorial, and only ``i``/``o``
        signals are present. If equal to 1, the I/O buffer is SDR, and only ``i``/``o`` signals are
        present. If greater than 1, the I/O buffer includes a gearbox, and ``iN``/``oN`` signals
        are present instead, where ``N in range(0, N)``. For example, if ``xdr=2``, the I/O buffer
        is DDR; the signal ``i0`` reflects the value at the rising edge, and the signal ``i1``
        reflects the value at the falling edge.
    path : tuple of str
        As in :class:`PureInterface`, used to name the created signals.

    Attributes
    ----------
    i_clk:
        I/O buffer input clock. Synchronizes `i*`. Present if ``xdr`` is nonzero.
    i_fclk:
        I/O buffer input fast clock. Synchronizes `i*` on higher gearbox ratios. Present if ``xdr``
        is greater than 2.
    i : Signal, out
        I/O buffer input, without gearing. Present if ``dir="i"`` or ``dir="io"``, and ``xdr`` is
        equal to 0 or 1.
    i0, i1, ... : Signal, out
        I/O buffer inputs, with gearing. Present if ``dir="i"`` or ``dir="io"``, and ``xdr`` is
        greater than 1.
    o_clk:
        I/O buffer output clock. Synchronizes `o*`, including `oe`. Present if ``xdr`` is nonzero.
    o_fclk:
        I/O buffer output fast clock. Synchronizes `o*` on higher gearbox ratios. Present if
        ``xdr`` is greater than 2.
    o : Signal, in
        I/O buffer output, without gearing. Present if ``dir="o"`` or ``dir="io"``, and ``xdr`` is
        equal to 0 or 1.
    o0, o1, ... : Signal, in
        I/O buffer outputs, with gearing. Present if ``dir="o"`` or ``dir="io"``, and ``xdr`` is
        greater than 1.
    oe : Signal, in
        I/O buffer output enable. Present if ``dir="io"`` or ``dir="oe"``. Buffers generally
        cannot change direction more than once per cycle, so at most one output enable signal
        is present.
    """

    @property
    def path(self) -> tuple[str | int, ...]:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def signature(self) -> Signature:
        ...

    class Signature(wiring.Signature):
        """A signature for :class:`Pin`.  The parameters are as defined on the ``Pin`` class,
        and are accessible as attributes.
        """
        def __init__(self, width: int, dir: str, *, xdr: int = ...) -> None:
            ...

        def __eq__(self, other) -> bool:
            ...

        def __repr__(self) -> str:
            ...

        def create(self, *, path: Optional[tuple[str | int, ...]] = ..., src_loc_at: int = ...) -> Pin:
            ...

    def __init__(self, width: int, dir: str, *, xdr: int = ..., name: Optional[str] = ..., path: Optional[tuple[str | int, ...]] = ..., src_loc_at: int = ...) -> None:
        ...

    @property
    def width(self) -> int:
        ...

    @property
    def dir(self) -> str:
        ...

    @property
    def xdr(self) -> int:
        ...
