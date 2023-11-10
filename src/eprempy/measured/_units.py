import typing

from ..metric import (
    Conversion,
)
from ._object import ObjectT


T = typing.TypeVar('T')


class Converter:
    """A callable interface to unit-conversion implementations."""

    def __init__(
        self,
        convert: typing.Callable[[Conversion, ObjectT], ObjectT],
    ) -> None:
        self._convert = convert

    def __call__(self, c: Conversion, x: ObjectT):
        """Apply conversion `c` to object `x`."""
        if c.old == c.new:
            return x
        return self._convert(c, x)


