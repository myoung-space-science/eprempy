import typing

from .. import metric
from ._context import (
    Context,
    context_factory as context,
)
from ._object import (
    Object,
    ObjectT,
)
from ._types import (
    Interface,
    Type,
)
from . import _factories
from . import _units as units
from . import _convert as convert
from ._sequence import Sequence
from ._value import Value


__all__ = [
    'Context',
    'Interface',
    'Object',
    'Object',
    'ObjectT',
    'Sequence',
    'Type',
    'Value',
    'units',
    'context',
    'convert',
]


T = typing.TypeVar('T')


@typing.overload
def value(
    x: typing.Any,
    /,
    unit: typing.Optional[metric.UnitLike],
) -> Value:
    """Create a measured value from input, if possible."""

@typing.overload
def value(x: T, /, unit: metric.UnitLike=typing.Literal['1']) -> Value[T]:
    """Create a measured value with the given unit."""

@typing.overload
def value(x: Value[T], /) -> Value[T]:
    """Create a measured value from an existing measured value."""

def value(x, /, unit=None) -> Value:
    return _factories.value_factory(x, unit=unit)


@typing.overload
def sequence(
    x: typing.Any,
    /,
    unit: typing.Optional[metric.UnitLike],
) -> Sequence:
    """Create a measured sequence from input, if possible."""

@typing.overload
def sequence(x: T, /, unit: metric.UnitLike=typing.Literal['1']) -> Sequence[T]:
    """Create a measured sequence with the given unit."""

@typing.overload
def sequence(x: Sequence[T], /) -> Sequence[T]:
    """Create a measured sequence from an existing measured sequence."""

def sequence(x, /, unit=None):
    return _factories.sequence_factory(x, unit=unit)


