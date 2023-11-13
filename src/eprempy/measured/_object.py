import typing

from .. import base
from .. import metric
from . import _types
from . import _context
from ..typehelp import Self


I = typing.TypeVar('I', bound=_types.Object)


class Object(_types.Object[base.RealType]):
    """An object with real-valued data and an associated metric unit."""

    def __init__(
        self,
        data: base.RealType,
        context: _context.Context[I],
    ) -> None:
        super().__init__(data, context.unit)
        self._context = context

    def withunit(self: Self, new: metric.UnitLike, /) -> Self:
        """Convert this object to a new unit."""
        return self._context.convert(self, new)

    @property
    def context(self):
        """This object's initialization context."""
        return self._context


ObjectT = typing.TypeVar('ObjectT', bound=Object)
"""Type variable bounded by `~measured.Object`."""


