from amaranth import ShapeCastable
from amaranth.lib.meta import Annotation
from amaranth.lib.memory import Memory, ReadPort, WritePort
from amaranth.lib.wiring import FlippedSignatureMembers, FlippedSignature, PureInterface, FlippedInterface, Component
from amaranth.lib.enum import EnumView, FlagView
from amaranth.lib.data import View, Const


__all__ = []


_to_patch = [
    ShapeCastable,
    Annotation,
    Memory,
    ReadPort,
    WritePort,
    FlippedSignatureMembers,
    FlippedSignature,
    PureInterface,
    FlippedInterface,
    Component,
    EnumView,
    FlagView,
    View,
    Const,
]


# Monkey-patch missing parametrizations
_subscription_stub = classmethod(lambda cls, *_: cls)
for cls in _to_patch:
    cls.__class_getitem__ = _subscription_stub  # type: ignore
