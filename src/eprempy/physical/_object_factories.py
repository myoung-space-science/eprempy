"""
Factory functions for physical objects.

This module defines all factory functions because many (though not all) factory
functions require knowledge of types other than their target type.
"""

import numbers
import typing

import numpy

from .. import measured
from .. import quantity
from .. import real
from ._scalar import Scalar
from ._tensor import Tensor
from ._vector import Vector
from ._array import (
    Array,
    converter,
)
from ._axis import Coordinates
from ._axes import (
    Axes,
    axes_factory,
)


@Scalar.register.factory
def scalar_factory(x, /, unit=None) -> Scalar:
    """Internal factory function for `~Scalar` instances."""
    d, u = scalar_args(x, unit)
    ctx = measured.context(u, measured.convert.singular)
    return Scalar(d, ctx)


def scalar_args(x, unit, /):
    """Parse arguments to initialize `~Scalar`."""
    if isinstance(x, Scalar):
        return x.data, x.unit
    if isinstance(x, numbers.Real):
        return x, unit
    a = numpy.array(x)
    s = a.size
    if s != 1:
        raise TypeError(
            f"Cannot create a scalar from data with size {s}"
        ) from None
    data = a[0]
    if isinstance(x, Tensor):
        return data, x.unit
    return data, unit


@Vector.register.factory
def vector_factory(x, /, unit=None) -> Vector:
    """Internal factory for `~Vector` instances."""
    d, u = vector_args(x, unit)
    ctx = measured.context(u, measured.convert.arraylike)
    return Vector(d, ctx)


def vector_args(x, unit, /):
    """Parse arguments to initialize `~Vector`."""
    if isinstance(x, (Vector, Coordinates)):
        return x.data, x.unit
    if isinstance(x, (quantity.Measurement, Scalar)):
        y = [x.data] if isinstance(x, Scalar) else x
        return vector_args(numpy.asarray(y), x.unit)
    if isinstance(x, Tensor):
        return vector_args(numpy.array(x.data), x.unit)
    a = numpy.asarray(x)
    if a.ndim != 1:
        raise TypeError(
            "Vector data must be one-dimensional"
        ) from None
    return a, unit


@Tensor.register.factory
def tensor_factory(x, /, unit=None) -> Tensor:
    """Internal factory for `~Tensor` instances."""
    d, u = tensor_args(x, unit)
    ctx = measured.context(u, measured.convert.arraylike)
    return Tensor(d, ctx)


def tensor_args(x, unit, /):
    """Parse arguments to initialize `~Tensor`."""
    if isinstance(x, Array):
        return x.data.array, x.unit
    if isinstance(x, Tensor):
        return x.data, x.unit
    if isinstance(x, (quantity.Measurement, Scalar)):
        y = [x.data] if isinstance(x, Scalar) else x
        return tensor_args(numpy.asarray(y), x.unit)
    a = numpy.asarray(x)
    if a.ndim == 0:
        raise TypeError(
            "Tensor data must have at least one dimension"
        ) from None
    return a, unit


@Array.register.factory
def array_factory(x, /, unit=None, axes=None) -> Array:
    """Internal factory for `~Array` instances."""
    d, u, b = array_args(x, unit, axes)
    ctx = measured.context(u, converter)
    return Array(d, ctx, b)


def array_args(x, unit, axes, /):
    """Parse arguments to initialize `~Array`."""
    if isinstance(x, Array):
        return x.data, x.unit, x.axes
    dimensions = tuple(axes or ())
    data = real.array(array_data(x), *dimensions)
    axes = array_axes(data.shape, axes)
    if isinstance(x, measured.Object):
        return data, x.unit, axes
    return data, unit, axes


def array_shape(x) -> typing.Tuple[int]:
    """Compute the shape of `x`."""
    if isinstance(x, (Tensor, real.Array, numpy.ndarray)):
        return x.shape
    if isinstance(x, Vector):
        return (x.size,)
    if isinstance(x, Scalar):
        return (1,)
    if shape := getattr(x, 'shape', None):
        return shape
    raise TypeError(
        f"Cannot determine shape of {x}"
    ) from None


def array_data(x):
    """Extract data for a physical array.

    Notes
    -----
    The behavior of this function depends on the type of argument.

    - If the argument is an instance of `~real.Array`, this function will
      extract the internal `_object` attribute rather than the `array` property,
      in order to avoid prematurely loading a large dataset into memory.
    - If the argument is an instance of a subclass of `~measured.Object`, this
      function will extract the `data` property (converting a scalar-like object
      to 1-D array, if necessary).
    - If the argument is an instance of `numpy.ndarray`, this function will
      immediately return it.
    - If the argument is a logically N-D sequence, this function will convert to
      an N-D `numpy.ndarray`.
    - If the argument is a complex number, this function will convert it to a
      1-D real-valued `numpy.ndarray`.
    - This function will immediately return all other types of objects. Notably,
      it will NOT attempt to convert an arbitrary object to a `numpy.ndarray` in
      case doing so would prematurely load a large dataset into memory.
    """
    if isinstance(x, real.Array):
        return x._object
    if isinstance(x, (Tensor, Vector, measured.Sequence)):
        return x.data
    if isinstance(x, (Scalar, measured.Value)):
        return numpy.array([x.data])
    if isinstance(x, numpy.ndarray):
        return x
    if isinstance(x, numbers.Complex):
        return numpy.array([float(x)])
    if isinstance(x, typing.Sequence):
        return numpy.array(x)
    return x # <- NetCDF, HDF, etc.


def array_axes(shape, axes) -> Axes:
    """Create axes from arguments."""
    if isinstance(axes, typing.Mapping):
        return axes_factory(axes)
    try:
        axes = axes_factory(shape=shape, dimensions=axes)
    except (TypeError, ValueError) as err:
        raise TypeError(
            "Cannot create array axes"
            f" from shape={shape} and axes={axes}"
        ) from err
    return axes


