import numpy

from ..metric import Conversion
from ._object import ObjectT


def arraylike(c: Conversion, x: ObjectT):
    """Unit-conversion implementation for array-like objects."""
    return apply(_scale_array, c, x)


def singular(c: Conversion, x: ObjectT):
    """Unit-conversion implementation for singular objects."""
    return apply(_scale_data, c, x)


def _scale_array(c: Conversion, x: ObjectT):
    """Convert `x.data` to an array before applying a conversion factor."""
    return float(c) * numpy.array(x)


def _scale_data(c: Conversion, x: ObjectT):
    """Directly apply a conversion factor to `x.data`."""
    return float(c) * x.data


def apply(f, c: Conversion, x: ObjectT):
    """Apply the given unit conversion to the given object."""
    if c.old == c.new:
        return x
    return x.spawn(f(c, x), unit=c.new)

