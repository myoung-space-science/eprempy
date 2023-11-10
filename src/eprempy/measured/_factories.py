import numbers
import typing

import numpy

from .. import metric
from ._context import (
    context_factory,
)
from ._object import Object
from ._value import Value
from ._sequence import Sequence
from . import _convert


@Value.register.factory
def value_factory(x, /, unit=None) -> Value:
    """Factory function for `~Value`."""
    d, u = value_args(x, unit)
    ctx = context_factory(u, _convert.singular)
    return Value(d, ctx)


def value_args(x, unit, /) -> typing.Tuple[typing.Any, metric.Unit]:
    """Parse arguments to initialize `~Value`."""
    if isinstance(x, Value):
        return x.data, x.unit
    if isinstance(x, (int, float, numbers.Real)):
        return x, unit
    if isinstance(x, (Sequence, numpy.ndarray)) and x.size == 1:
        if isinstance(x, Sequence):
            return x.data[0], x.unit
        if isinstance(x, numpy.ndarray):
            return value_args(numpy.ravel(x)[0], unit)
    if isinstance(x, typing.Sequence) and not isinstance(x, str):
        return value_args(numpy.array(x), unit)
    raise TypeError(
        f"Cannot create a value from {x!r} and {unit!r}"
    ) from None


@Sequence.register.factory
def sequence_factory(x, /, unit=None) -> Sequence:
    """Factory function for `~Sequence`."""
    d, u = sequence_args(x, unit)
    ctx = context_factory(u, _convert.arraylike)
    return Sequence(d, ctx)


def sequence_args(x, unit, /) -> typing.Tuple[typing.Any, metric.Unit]:
    """Parse arguments to initialize `~Sequence`."""
    if isinstance(x, Value):
        return sequence_args([x.data], x.unit)
    if isinstance(x, Object):
        return x.data, x.unit
    if isinstance(x, numbers.Real):
        return numpy.array([x]), unit
    a = numpy.asarray(x)
    if a.ndim > 0:
        return a.flatten(), unit
    raise TypeError(
        f"Cannot create a sequence from {x!r} and {unit!r}"
    ) from None


