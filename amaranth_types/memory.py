
from collections.abc import Iterable
from amaranth import *
from typing import Any, Generic, Optional, Protocol, TypeVar
from amaranth.hdl import ValueCastable

from amaranth_types.types import HasElaborate, ShapeLike, ValueLike


__all__ = ["AbstractMemory", "AbstractReadPort", "AbstractWritePort", "AbstractMemoryConstructor"]

_T_ValueOrValueCastable = TypeVar("_T_ValueOrValueCastable", bound=Value | ValueCastable, covariant=True)
_T_Cov_ShapeLike = TypeVar("_T_Cov_ShapeLike", bound=ShapeLike, covariant=True)
_T_ShapeLike = TypeVar("_T_ShapeLike", bound=ShapeLike)


class AbstractReadPort(Generic[_T_Cov_ShapeLike, _T_ValueOrValueCastable], Protocol):
    @property
    def en(self) -> Signal:
        ...

    @property
    def addr(self) -> Signal:
        ...

    @property
    def data(self) -> _T_ValueOrValueCastable:
        ...


class AbstractWritePort(Generic[_T_Cov_ShapeLike, _T_ValueOrValueCastable], Protocol):
    @property
    def en(self) -> Signal:
        ...

    @property
    def addr(self) -> Signal:
        ...

    @property
    def data(self) -> _T_ValueOrValueCastable:
        ...


class AbstractMemory(Generic[_T_Cov_ShapeLike, _T_ValueOrValueCastable], HasElaborate, Protocol):
    @property
    def shape(self) -> ShapeLike:
        ...

    @property
    def depth(self) -> int:
        ...

    def read_port(
        self,
        *,
        domain: str = ...,
        transparent_for: Iterable[Any] = ...,
        src_loc_at: int = ...
    ) -> AbstractReadPort[_T_Cov_ShapeLike, _T_ValueOrValueCastable]:
        ...

    def write_port(
        self,
        *,
        domain: str = ...,
        granularity: Optional[int] = ...,
        src_loc_at: int = ...
    ) -> AbstractWritePort[_T_Cov_ShapeLike, _T_ValueOrValueCastable]:
        ...


class AbstractMemoryConstructor(Generic[_T_ShapeLike, _T_ValueOrValueCastable], Protocol):
    @staticmethod
    def __call__(
        *,
        shape: _T_ShapeLike,
        depth: int,
        init: Iterable[ValueLike],
        attrs: Optional[dict[str, str]] = ...,
        src_loc_at: int = ...
    ) -> AbstractMemory[_T_ShapeLike, _T_ValueOrValueCastable]:
        ...
