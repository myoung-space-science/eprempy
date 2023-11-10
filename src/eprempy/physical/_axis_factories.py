import numbers
import typing

import numpy
import numpy.typing

from .. import measured
from ._axis import (
    Points,
    Symbols,
    Coordinates,
)


@Points.register.factory
def points_factory(x, /):
    """Internal factory for `~Points` instances."""
    return Points(points_args(x))


def points_args(x, /) -> numpy.typing.NDArray[numpy.uint]:
    """Parse arguments to initialize `~Points`."""
    if isinstance(x, Points):
        return x.data
    try:
        # XXX: Creating this intermediate array circumvents bugs that arise when
        # `x.__array__` does not accept arguments.
        tmp = numpy.array(x)
    except (ValueError, TypeError) as err:
        raise TypeError(
            f"Cannot initialize {Points} from {x}"
        ) from err
    data = numpy.array(tmp, ndmin=1, dtype=int)
    if any(i < 0 for i in data):
        raise TypeError(
            f"Cannot initialize {Points} from an object"
            " with negative values"
        ) from None
    return data


@Symbols.register.factory
def symbols_factory(x, /):
    """Internal factory for `~Symbols` instances."""
    return Symbols(symbols_args(x))


def symbols_args(x, /) -> typing.List[str]:
    """Parse arguments to initialize `~Symbols`."""
    if isinstance(x, Symbols):
        return x.data
    if isinstance(x, str):
        return [x]
    if not isinstance(x, typing.Sequence):
        raise TypeError(
            f"Cannot initialize {Symbols} from non-sequence"
            f" type {type(x)}"
        ) from None
    if not all(isinstance(i, str) for i in x):
        raise TypeError(
            f"Cannot initialize {Symbols} from sequence"
            " with non-string members"
        ) from None
    return x


@Coordinates.register.factory
def coordinates_factory(x, /):
    """Internal factory for `~Coordinates` instances."""
    return Coordinates(coordinates_args(x))


def coordinates_args(x, /) -> measured.Sequence[numbers.Real]:
    """Parse arguments to initialize `~Coordinates`."""
    if isinstance(x, Coordinates):
        return x.data
    try:
        s = measured.sequence(x)
    except TypeError as err:
        raise TypeError(
            f"Cannot initialize {Coordinates} from {x}"
        ) from err
    return s


