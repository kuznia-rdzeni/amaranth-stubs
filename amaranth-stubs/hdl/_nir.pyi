"""
This type stub file was generated by pyright.
"""

import enum
from typing import Iterable

"""
This type stub file was generated by pyright.
"""
__all__ = ["Net", "Value", "IONet", "IOValue", "FormatValue", "Format", "Netlist", "ModuleNetFlow", "IODirection", "Module", "Cell", "Top", "Operator", "Part", "Matches", "PriorityMatch", "Assignment", "AssignmentList", "FlipFlop", "Memory", "SyncWritePort", "AsyncReadPort", "SyncReadPort", "AsyncPrint", "SyncPrint", "Initial", "AnyValue", "AsyncProperty", "SyncProperty", "Instance", "IOBuffer"]
class Net(int):
    __slots__ = ...
    @classmethod
    def from_cell(cls, cell: int, bit: int):
        ...
    
    @classmethod
    def from_const(cls, val: int):
        ...
    
    @classmethod
    def from_late(cls, val: int):
        ...
    
    @property
    def is_const(self):
        ...
    
    @property
    def const(self):
        ...
    
    @property
    def is_late(self):
        ...
    
    @property
    def is_cell(self):
        ...
    
    @property
    def cell(self):
        ...
    
    @property
    def bit(self):
        ...
    
    @classmethod
    def ensure(cls, value: Net):
        ...
    
    def __repr__(self):
        ...
    
    __str__ = ...


class Value(tuple):
    __slots__ = ...
    def __new__(cls, nets: Net | Iterable[Net] = ...):
        ...
    
    @classmethod
    def from_const(cls, value, width):
        ...
    
    @classmethod
    def zeros(cls, digits=...):
        ...
    
    @classmethod
    def ones(cls, digits=...):
        ...
    
    def __getitem__(self, index):
        ...
    
    def __repr__(self):
        ...
    
    @property
    def is_const(self):
        ...
    
    __str__ = ...


class IONet(int):
    __slots__ = ...
    @classmethod
    def from_port(cls, port: int, bit: int):
        ...
    
    @property
    def port(self):
        ...
    
    @property
    def bit(self):
        ...
    
    @classmethod
    def ensure(cls, value: IONet):
        ...
    
    def __repr__(self):
        ...
    
    __str__ = ...


class IOValue(tuple):
    __slots__ = ...
    def __new__(cls, nets: IONet | Iterable[IONet] = ...):
        ...
    
    def __getitem__(self, index):
        ...
    
    def __repr__(self):
        ...
    
    __str__ = ...


class FormatValue:
    """A single formatted value within ``Format``.

    Attributes
    ----------

    value: Value
    format_desc: str
    signed: bool
    """
    def __init__(self, value, format_desc, *, signed) -> None:
        ...
    
    def __repr__(self):
        ...
    


class Format:
    """Like _ast.Format, but for NIR.

    Attributes
    ----------

    chunks: tuple of str and FormatValue
    """
    def __init__(self, chunks) -> None:
        ...
    
    def __repr__(self):
        ...
    
    def input_nets(self):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    


class Netlist:
    """A fine netlist. Consists of:

    - a flat array of cells
    - a dictionary of connections for late-bound nets
    - a map of hierarchical names to nets
    - a map of signals to nets

    The nets are virtual: a list of nets is not materialized anywhere in the netlist.
    A net is a single bit wide and represented as a single int. The int is encoded as follows:

    - A negative number means a late-bound net. The net should be looked up in the ``connections``
      dictionary to find its driver.
    - Non-negative numbers are cell outputs, and are split into bitfields as follows:

      - bits 0-15: output bit index within a cell (exact meaning is cell-dependent)
      - bits 16-...: index of cell in ``netlist.cells``

    Cell 0 is always ``Top``.  The first two output bits of ``Top`` are considered to be constants
    ``0`` and ``1``, which effectively means that net encoded as ``0`` is always a constant ``0`` and
    net encoded as ``1`` is always a constant ``1``.

    Multi-bit values are represented as tuples of int.

    Attributes
    ----------

    modules : list of ``Module``
    cells : list of ``Cell``
    connections : dict of (negative) int to int
    io_ports : list of ``IOPort``
    signals : dict of Signal to ``Value``
    last_late_net: int
    """
    def __init__(self) -> None:
        ...
    
    def resolve_net(self, net: Net):
        ...
    
    def resolve_value(self, value: Value):
        ...
    
    def resolve_all_nets(self):
        ...
    
    def __repr__(self):
        ...
    
    def add_module(self, parent, name: str, *, src_loc=..., cell_src_loc=...):
        ...
    
    def add_cell(self, cell):
        ...
    
    def add_value_cell(self, width: int, cell):
        ...
    
    def alloc_late_value(self, width: int):
        ...
    
    @property
    def top(self):
        ...
    


class ModuleNetFlow(enum.Enum):
    """Describes how a given Net flows into or out of a Module.

    The net can also be none of these (not present in the dictionary at all),
    when it is not present in the module at all.
    """
    Internal = ...
    Input = ...
    Output = ...


class IODirection(enum.Enum):
    Input = ...
    Output = ...
    Bidir = ...
    def __or__(self, other):
        ...
    


class Module:
    """A module within the netlist.

    Attributes
    ----------

    parent: index of parent module, or ``None`` for top module
    name: a tuple of str, hierarchical name of this module (top has empty tuple)
    src_loc: str
    submodules: a list of nested module indices
    signal_names: a SignalDict from Signal to str, signal names visible in this module
    net_flow: a dict from Net to NetFlow, describes how a net is used within this module
    ports: a dict from port name to (Value, ModuleNetFlow) pair
    io_ports: a dict from port name to (IOValue, IODirection) pair
    cells: a list of cell indices that belong to this module
    """
    def __init__(self, parent, name, *, src_loc, cell_src_loc) -> None:
        ...
    


class Cell:
    """A base class for all cell types.

    Attributes
    ----------

    src_loc: str
    module: int, index of the module this cell belongs to (within Netlist.modules)
    """
    def __init__(self, module_idx: int, *, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def io_nets(self):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    


class Top(Cell):
    """A special cell type representing top-level non-IO ports. Must be present in the netlist exactly
    once, at index 0.

    Top-level outputs are stored as a dict of names to their assigned values.

    Top-level inputs are effectively the output of this cell. They are stored
    as a dict of names to a (start bit index, width) tuple. Output bit indices 0 and 1 are reserved
    for constant nets, so the lowest bit index that can be assigned to a port is 2.

    Attributes
    ----------

    ports_o: dict of str to Value
    ports_i: dict of str to (int, int)
    """
    def __init__(self) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class Operator(Cell):
    """Roughly corresponds to ``hdl.ast.Operator``.

    The available operators are roughly the same as in AST, with some changes:

    - '<', '>', '<=', '>=', '//', '%', '>>' have signed and unsigned variants that are selected
      by prepending 'u' or 's' to operator name
    - 's', 'u', and unary '+' are redundant and do not exist
    - many operators restrict input widths to be the same as output width,
      and/or to be the same as each other

    The unary operators are:

    - '-', '~': like AST, input same width as output
    - 'b', 'r|', 'r&', 'r^': like AST, 1-bit output

    The binary operators are:

    - '+', '-', '*', '&', '^', '|', 'u//', 's//', 'u%', 's%': like AST, both inputs same width as output
    - '<<', 'u>>', 's>>': like AST, first input same width as output
    - '==', '!=', 'u<', 's<', 'u>', 's>', 'u<=', 's<=', 'u>=', 's>=': like AST, both inputs need to have
      the same width, 1-bit output

    The ternary operators are:

    - 'm': multiplexer, first input needs to have width of 1, second and third operand need to have 
      the same width as output; implements arg0 ? arg1 : arg2

    Attributes
    ----------

    operator: str, symbol of the operator (from the above list)
    inputs: tuple of Value
    """
    def __init__(self, module_idx, *, operator: str, inputs, src_loc) -> None:
        ...
    
    @property
    def width(self):
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class Part(Cell):
    """Corresponds to ``hdl.ast.Part``.

    Attributes
    ----------

    value: Value, the data input
    value_signed: bool
    offset: Value, the offset input
    width: int
    stride: int
    """
    def __init__(self, module_idx, *, value, value_signed, offset, width, stride, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class Matches(Cell):
    """A combinatorial cell performing a comparison like ``Value.matches``
    (or, equivalently, a case condition).

    Attributes
    ----------

    value: Value
    patterns: tuple of str, each str contains '0', '1', '-'
    """
    def __init__(self, module_idx, *, value, patterns, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class PriorityMatch(Cell):
    """Used to represent a single switch on the control plane of processes.

    The output is the same length as ``inputs``. If ``en`` is ``0``, the output
    is all-0. Otherwise, output keeps the lowest-numbered ``1`` bit in the input
    (if any) and masks all other bits to ``0``.

    Note: the RTLIL backend requires all bits of ``inputs`` to be driven
    by a ``Match`` cell within the same module.

    Attributes
    ----------
    en: Net
    inputs: Value
    """
    def __init__(self, module_idx, *, en, inputs, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class Assignment:
    """A single assignment in an ``AssignmentList``.

    The assignment is executed iff ``cond`` is true. When the assignment
    is executed, ``len(value)`` bits starting at position `offset` are set
    to the value ``value``, and the remaining bits are unchanged.
    Assignments to out-of-bounds bit indices are ignored.

    Attributes
    ----------

    cond: Net
    start: int
    value: Value
    src_loc: str
    """
    def __init__(self, *, cond, start, value, src_loc) -> None:
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class AssignmentList(Cell):
    """Used to represent a single assigned signal on the data plane of processes.

    The output of this cell is determined by starting with the ``default`` value,
    then executing each assignment in sequence.

    Note: the RTLIL backend requires all ``cond`` inputs of assignments to be driven
    by a ``PriorityMatch`` cell within the same module.

    Attributes
    ----------
    default: Value
    assignments: tuple of ``Assignment``
    """
    def __init__(self, module_idx, *, default, assignments, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class FlipFlop(Cell):
    """A flip-flop. ``data`` is the data input. ``init`` is the initial and async reset value.
    ``clk`` and ``clk_edge`` work as in a ``ClockDomain``. ``arst`` is the async reset signal,
    or ``0`` if async reset is not used.

    Attributes
    ----------

    data: Value
    init: int
    clk: Net
    clk_edge: str, either 'pos' or 'neg'
    arst: Net
    attributes: dict from str to int, Const, or str
    """
    def __init__(self, module_idx, *, data, init, clk, clk_edge, arst, attributes, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class Memory(Cell):
    """Corresponds to ``Memory``.  ``init`` must have length equal to ``depth``.
    Read and write ports are separate cells.

    Attributes
    ----------

    width: int
    depth: int
    init: tuple of int
    name: str
    attributes: dict from str to int, Const, or str
    """
    def __init__(self, module_idx, *, width, depth, init, name, attributes, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class SyncWritePort(Cell):
    """A single write port of a memory.  This cell has no output.

    Attributes
    ----------

    memory: cell index of ``Memory``
    data: Value
    addr: Value
    en: Value
    clk: Net
    clk_edge: str, either 'pos' or 'neg'
    """
    def __init__(self, module_idx, memory, *, data, addr, en, clk, clk_edge, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class AsyncReadPort(Cell):
    """A single asynchronous read port of a memory.

    Attributes
    ----------

    memory: cell index of ``Memory``
    width: int
    addr: Value
    """
    def __init__(self, module_idx, memory, *, width, addr, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class SyncReadPort(Cell):
    """A single synchronous read port of a memory.  The cell output is the data port.
    ``transparent_for`` is the set of write ports (identified by cell index) that this
    read port is transparent with.

    Attributes
    ----------

    memory: cell index of ``Memory``
    width: int
    addr: Value
    en: Net
    clk: Net
    clk_edge: str, either 'pos' or 'neg'
    transparent_for: tuple of int
    """
    def __init__(self, module_idx, memory, *, width, addr, en, clk, clk_edge, transparent_for, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class AsyncPrint(Cell):
    """Corresponds to ``Print`` in the "comb" domain.

    Attributes
    ----------

    en: Net
    format: Format
    """
    def __init__(self, module_idx, *, en, format, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class SyncPrint(Cell):
    """Corresponds to ``Print`` in domains other than "comb".

    Attributes
    ----------

    en: Net
    clk: Net
    clk_edge: str, either 'pos' or 'neg'
    format: Format
    """
    def __init__(self, module_idx, *, en, clk, clk_edge, format, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class Initial(Cell):
    """Corresponds to ``Initial`` value."""
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class AnyValue(Cell):
    """Corresponds to ``AnyConst`` or ``AnySeq``. ``kind`` must be either ``'anyconst'``
    or ``'anyseq'``.

    Attributes
    ----------

    kind: str, 'anyconst' or 'anyseq'
    width: int
    """
    def __init__(self, module_idx, *, kind, width, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class AsyncProperty(Cell):
    """Corresponds to ``Assert``, ``Assume``, or ``Cover`` in the "comb" domain.

    Attributes
    ----------

    kind: str, either 'assert', 'assume', or 'cover'
    test: Net
    en: Net
    format: Format or None
    """
    def __init__(self, module_idx, *, kind, test, en, format, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class SyncProperty(Cell):
    """Corresponds to ``Assert``, ``Assume``, or ``Cover`` in domains other than "comb".

    Attributes
    ----------

    kind: str, either 'assert', 'assume', or 'cover'
    test: Net
    en: Net
    clk: Net
    clk_edge: str, either 'pos' or 'neg'
    format: Format or None
    """
    def __init__(self, module_idx, *, kind, test, en, clk, clk_edge, format, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class Instance(Cell):
    """Corresponds to ``Instance``. ``type``, ``parameters`` and ``attributes`` work the same as in
    ``Instance``. Input and inout ports are represented as a dict of port names to values.
    Inout ports must be connected to nets corresponding to an IO port of the ``Top`` cell.

    Output ports are represented as a dict of port names to (start bit index, width) describing
    their position in the virtual "output" of this cell.

    Attributes
    ----------

    type: str
    name: str
    parameters: dict of str to Const, int, or str
    attributes: dict of str to Const, int, or str
    ports_i: dict of str to Value
    ports_o: dict of str to pair of int (index start, width)
    ports_io: dict of str to (IOValue, IODirection)
    """
    def __init__(self, module_idx, *, type, name, parameters, attributes, ports_i, ports_o, ports_io, src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def io_nets(self):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


class IOBuffer(Cell):
    """An IO buffer cell. This cell does two things:

    - a tristate buffer is inserted driving ``port`` based on ``o`` and ``oe`` nets (output buffer)
    - the value of ``port`` is sampled and made available as output of this cell (input buffer)

    Attributes
    ----------

    port: IOValue
    dir: IODirection
    o: Value or None
    oe: Net or None
    """
    def __init__(self, module_idx, *, port, dir, o=..., oe=..., src_loc) -> None:
        ...
    
    def input_nets(self):
        ...
    
    def output_nets(self, self_idx: int):
        ...
    
    def io_nets(self):
        ...
    
    def resolve_nets(self, netlist: Netlist):
        ...
    
    def __repr__(self):
        ...
    


