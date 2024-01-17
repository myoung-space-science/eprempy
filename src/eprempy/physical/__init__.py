import numbers
import typing

from .. import measured
from .. import metric
from .. import real
from .. import quantity
from ._object import (
    Object,
    ObjectT as ObjectType,
)
from ._axis import (
    Axis,
    AxisTypeError,
    AxisValueError,
    Points,
    Symbols,
    Coordinates,
)
from ._axes import (
    AxisType,
    Axes,
)
from . import _object_factories
from . import _axis_factories
from ._types import (
    ArrayType,
    QuantityType,
)
# NOTE: Importing these objects from _operations.py (instead of from their
# respective modules) has the **necessary** side-effect of running the code that
# implements all operators on physical objects.
from ._operations import (
    Scalar,
    Tensor,
    Vector,
    Array,
)


__all__ = [
    'Axis',
    'AxisTypeError',
    'AxisValueError',
    'Axes',
    'Points',
    'Symbols',
    'Coordinates',
    'Object',
    'ObjectType',
    'QuantityType',
    'ArrayType',
    'Scalar',
    'scalar',
    'Tensor',
    'tensor',
    'Vector',
]


@typing.overload
def scalar(
    x: typing.Any,
    /,
    unit: typing.Optional[metric.UnitLike]=None,
) -> Scalar:
    """Create a physical scalar from the given arguments, if possible"""

@typing.overload
def scalar(
    x: typing.Union[real.ValueType, typing.Sequence[real.ValueType]],
    /,
) -> Scalar[real.ValueType]:
    """Create a unitless physical scalar from a real number.

    Parameters
    ----------
    x : real number or equivalent length-1 sequence
        The numeric value of the new scalar, or a length-1 sequence containing
        the numeric value of the new scalar.

    Returns
    -------
    `~Scalar`
        A new physical scalar with the given value, and a unit equal to '1'.

    Raises
    ------
    `TypeError`
        The argument is a sequence with length > 1.
    """

@typing.overload
def scalar(
    x: typing.Union[real.ValueType, typing.Sequence[real.ValueType]],
    /,
    unit: metric.UnitLike,
) -> Scalar[real.ValueType]:
    """Create a physical scalar from a real number and a unit.

    Parameters
    ----------
    x : real number or equivalent length-1 sequence
        The numeric value of the new scalar, or a length-1 sequence containing
        the numeric value of the new scalar.
    unit : unit-like
        The metric unit associated with `x`.

    Returns
    -------
    `~Scalar`
        A new physical scalar with the given value and unit.

    Raises
    ------
    `TypeError`
        The argument to `x` is a sequence with length > 1.
    """

@typing.overload
def scalar(x: Scalar[real.ValueType], /) -> Scalar[real.ValueType]:
    """Create a physical scalar from a physical scalar.

    Parameters
    ----------
    x : `~Scalar`
        The scalar from which to create a new scalar. This function will make a
        copy of `x`.

    Returns
    -------
    `~Scalar`
        A new physical scalar with value and unit taken from the given scalar.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

@typing.overload
def scalar(x: Tensor[real.ValueType], /) -> Scalar[real.ValueType]:
    """Create a physical scalar from a physical tensor.

    Parameters
    ----------
    x : `~Tensor`
        The tensor from which to create a new scalar. The tensor must be
        singular (i.e., its data must comprise a single value).

    Returns
    -------
    `~Scalar`
        A new physical scalar with value and unit taken from the given tensor.

    Raises
    ------
    `TypeError`
        The given tensor is not singular.
    `ValueError`
        The caller passed an explicit unit.
    """

def scalar(x, /, unit=None):
    return _object_factories.scalar_factory(x, unit=unit)


@typing.overload
def vector(
    x: typing.Any,
    /,
    unit: typing.Optional[metric.UnitLike]=None,
) -> Vector:
    """Create a physical vector from the given arguments, if possible"""

@typing.overload
def vector(x: typing.Sequence[real.ValueType], /) -> Vector[real.ValueType]:
    """Create a unitless physical vector from a real-valued sequence.

    Parameters
    ----------
    x : sequence of `int`, `float`, or `numbers.Real`
        The numeric value(s) of the new vector. This function will convert the
        given sequence to a `numpy.ndarray` if necessary.

    Returns
    -------
    `~Vector`
        A new physical vector with the given value(s), and a unit equal to
        '1'.

    Raises
    ------
    `TypeError`
        The input is not logically 1-dimensional.
    """

@typing.overload
def vector(
    x: typing.Sequence[real.ValueType],
    /,
    unit: metric.UnitLike,
) -> Vector[real.ValueType]:
    """Create a physical vector from a real-valued sequence and a unit.

    Parameters
    ----------
    x : sequence of `int`, `float`, or `numbers.Real`
        The numeric value(s) of the new vector. This function will convert the
        given sequence to a `numpy.ndarray` if necessary.
    unit : unit-like
        The metric unit associated with `x`.

    Returns
    -------
    `~Vector`
        A new physical vector with the given value(s) and unit.

    Raises
    ------
    `TypeError`
        The input is not logically 1-dimensional.
    """

@typing.overload
def vector(x: Vector[real.ValueType], /) -> Vector[real.ValueType]:
    """Create a physical vector from an existing physical vector.

    Parameters
    ----------
    x : `~Vector`
        The vector from which to create a new vector. This function will
        make a copy of `x`.

    Returns
    -------
    `~Vector`
        A new physical vector with value and unit taken from the given
        vector.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

@typing.overload
def vector(x: Tensor[real.ValueType], /) -> Vector[real.ValueType]:
    """Create a physical vector from an existing physical tensor.

    Parameters
    ----------
    x : `~Tensor`
        A 1-dimensional tensor from which to create a new vector.

    Returns
    -------
    `~Vector`
        A new physical vector with value and unit taken from the given tensor.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

@typing.overload
def vector(x: Scalar[real.ValueType], /) -> Vector[real.ValueType]:
    """Create a physical vector from an existing physical scalar.

    Parameters
    ----------
    x : `~Scalar`
        The scalar from which to create a new vector. This function will
        convert the scalar's data value into a 1-element `numpy.ndarray`.

    Returns
    -------
    `~Vector`
        A new physical vector with value and unit taken from the given scalar.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

@typing.overload
def vector(
    x: quantity.Measurement[real.ValueType],
    /,
) -> Vector[real.ValueType]:
    """Create a physical vector from an existing measurement.

    Parameters
    ----------
    x : `~quantity.Measurement`
        The measurement from which to create a new vector. This function will
        convert the measurement's data into a `numpy.ndarray` if necessary.

    Returns
    -------
    `~Vector`
        A new physical vector with data and unit taken from the given
        measurement.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

def vector(x, /, unit=None):
    return _object_factories.vector_factory(x, unit=unit)


@typing.overload
def tensor(
    x: typing.Any,
    /,
    unit: typing.Optional[metric.UnitLike]=None,
) -> Tensor:
    """Create a physical tensor from the given arguments, if possible"""

@typing.overload
def tensor(x: typing.Sequence[real.ValueType], /) -> Tensor[real.ValueType]:
    """Create a unitless physical tensor from a real-valued sequence.

    Parameters
    ----------
    x : sequence of `int`, `float`, or `numbers.Real`
        The numeric value(s) of the new tensor. This function will convert the
        given sequence to a `numpy.ndarray` if necessary.

    Returns
    -------
    `~Tensor`
        A new physical tensor with the given value(s), and a unit equal to '1'.

    Raises
    ------
    `TypeError`
        The input produced a rank-0 tensor.
    """

@typing.overload
def tensor(
    x: typing.Sequence[real.ValueType],
    /,
    unit: metric.UnitLike,
) -> Tensor[real.ValueType]:
    """Create a physical tensor from a real-valued sequence and a unit.

    Parameters
    ----------
    x : sequence of `int`, `float`, or `numbers.Real`
        The numeric value(s) of the new tensor. This function will convert the
        given sequence to a `numpy.ndarray` if necessary.
    unit : unit-like
        The metric unit associated with `x`.

    Returns
    -------
    `~Tensor`
        A new physical tensor with the given value(s) and unit.

    Raises
    ------
    `TypeError`
        The input produced a rank-0 tensor.
    """

@typing.overload
def tensor(x: Tensor[real.ValueType], /) -> Tensor[real.ValueType]:
    """Create a physical tensor from an existing physical tensor.

    Parameters
    ----------
    x : `~Tensor`
        The tensor from which to create a new tensor. This function will make a
        copy of `x`.

    Returns
    -------
    `~Tensor`
        A new physical tensor with value and unit taken from the given tensor.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

@typing.overload
def tensor(x: Scalar[real.ValueType], /) -> Tensor[real.ValueType]:
    """Create a physical tensor from an existing physical scalar.

    Parameters
    ----------
    x : `~Scalar`
        The scalar from which to create a new tensor. This function will convert
        the scalar's data value into a 1-element `numpy.ndarray`.

    Returns
    -------
    `~Tensor`
        A new physical tensor with value and unit taken from the given scalar.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

@typing.overload
def tensor(
    x: quantity.Measurement[real.ValueType],
    /,
) -> Tensor[real.ValueType]:
    """Create a physical tensor from an existing measurement.

    Parameters
    ----------
    x : `~quantity.Measurement`
        The measurement from which to create a new tensor. This function will
        convert the measurement's data into a `numpy.ndarray` if necessary.

    Returns
    -------
    `~Tensor`
        A new physical tensor with data and unit taken from the given
        measurement.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

def tensor(x, /, unit=None):
    return _object_factories.tensor_factory(x, unit=unit)


@typing.overload
def points(
    x: typing.Union[
        typing.SupportsInt,
        typing.Sequence[typing.SupportsInt],
        Points,
    ],
    /,
) -> Points:
    """Create an integral axis.

    Parameters
    ----------
    TODO
    """

def points(x, /):
    return _axis_factories.points_factory(x)

@typing.overload
def symbols(
    x: typing.Union[str, typing.Sequence[str], Symbols],
    /,
) -> Symbols:
    """Create a symbolic axis.

    Parameters
    ----------
    TODO
    """

def symbols(x, /):
    return _axis_factories.symbols_factory(x)


@typing.overload
def coordinates(
    x: typing.Union[
        numbers.Real,
        typing.Sequence[numbers.Real],
        Coordinates,
    ],
    /,
) -> Coordinates:
    """Create a coordinate axis.

    Parameters
    ----------
    TODO
    """

def coordinates(x, /):
    return _axis_factories.coordinates_factory(x)


@typing.overload
def axes(
    mapping: typing.Mapping[str, AxisType],
    *lengths: numbers.Integral,
    shape: typing.Optional[typing.Iterable[numbers.Integral]]=None,
    dimensions: typing.Optional[typing.Iterable[str]]=None,
    axes: typing.Optional[typing.Iterable[AxisType]]=None,
    **pairs: AxisType
) -> Axes:
    """Create a axes from arguments. See Notes for precedence rules.

    Returns
    -------
    `~axes`

    Raises
    ------
    `ValueError`
        The given combination of arguments produced an empty axes.
    `TypeError`
        The caller passed `shape` or `axes` as a positional argument.

    Notes
    -----
    - A axes initialized from only a shape will contain axis pairs in which
      each name has the form `xi` and the corresponding sequence is a length-`i`
      zero-based integer array, where `i` ranges from 0 to `len(shape)-1`.
    - A axes initialized from a sequence of anonymous axes will contain
      key-value pairs with keys constructed as if initialized from a shape, each
      corresponding to an axis in the order given.
    - Explicit dimensions will replace default axis names in a axes initialized
      from either a shape or axes.
    - A axes initialized from key-value pairs or from a single mapping will use
      each key as a dimension and the corresponding value as the axis object.
    - In case of multiple initialization styles, key-value pairs take precedence
      over a mapping, which takes precedence over axes (with or without explicit
      dimensions), which take precedence over shape (with or without explicit
      dimensions).
    """

@typing.overload
def axes(*lengths: numbers.Integral) -> Axes:
    """Create a axes with the given axis lengths.

    Parameters
    ----------
    *lengths : integral numbers
        One or more integral axis lengths.

    Returns
    -------
    `~axes`
    """

@typing.overload
def axes(
    *,
    shape: typing.Iterable[numbers.Integral],
    dimensions: typing.Iterable[str],
) -> Axes:
    """Create a axes with the given shape.

    Parameters
    ----------
    shape : iterable of integral numbers
        An iterable object containing one or more integral axis lengths. Must be
        passed as a keyword argument.
    dimensions : iterable of strings
        The name of each axis. The length of `dimensions` must equal the length
        of `shape`. Must be passed as a keyword argument.

    Returns
    -------
    `~axes`

    Raises
    ------
    `TypeError`
        Caller passed dimensions without shape.
    `ValueError`
        Caller passed dimensions and shape with different lengths.
    """

@typing.overload
def axes(
    *,
    dimensions: typing.Iterable[str],
    axes: typing.Iterable[AxisType],
) -> Axes:
    """Create a axes from anonymous axes.

    Parameters
    ----------
    dimensions : iterable of strings
        The name of each axis. The length of `dimensions` must equal the length
        of `axes`. Must be passed as a keyword argument.
    axes : iterable of axis-like
        An iterable object containing one or more axis-like objects. Each
        argument may be an iterable of integers or an instance of `~Axis`. Must
        be passed as a keyword argument.

    Returns
    -------
    `~axes`

    Raises
    ------
    `TypeError`
        Caller passed dimensions without shape.
    `ValueError`
        Caller passed dimensions and shape with different lengths.
    """

@typing.overload
def axes(**pairs: AxisType) -> Axes:
    """Create a axes from individual dimension-axis pairs.

    Parameters
    ----------
    **pairs
        One or more key-value pairs. Each value may be an iterable of integers
        or an instance of `~Axis`. The corresponding key will become the string
        dimension corresponding to that axis.

    Returns
    -------
    `~axes`
    """

@typing.overload
def axes(mapping: typing.Mapping[str, AxisType]) -> Axes:
    """Create a axes from a mapping of dimension-axis pairs.

    Parameters
    ----------
    mapping
        A mapping from dimension name to axis value. Each value may be an
        iterable of integers or an instance of `~Axis`. The corresponding key
        will become the string dimension corresponding to that axis.

    Returns
    -------
    `~axes`
    """

def axes(*args, **kwargs):
    return _axes.axes_factory(*args, **kwargs)


DimensionsLike = typing.Iterable[str]

AxesLike = typing.Mapping[str, AxisType]

@typing.overload
def array(x: typing.Any, **kwargs) -> Array:
    """Create a physical array from the given arguments, if possible"""

@typing.overload
def array(
    x: typing.Sequence[real.ValueType],
    /,
    unit: typing.Optional[metric.UnitLike]=None,
    axes: typing.Optional[typing.Union[DimensionsLike, AxesLike]]=None,
) -> Array:
    """Create a physical array from a real-valued sequence.

    Parameters
    ----------
    x : array-like sequence of real numbers
        The numerical data of the new array.
    unit : unit-like
        The metric unit associated with values in `x`.
    axes : dimensions-like or axes-like
        Either an iterable of string dimensions (i.e., axis names) or a mapping
        from dimension to axis vector. The number of axes must equal the number
        of logical dimensions in `x`.

    Returns
    -------
    `~Array`
    """

@typing.overload
def array(
    x: measured.Object[real.ValueType],
    /,
    axes: typing.Optional[typing.Union[DimensionsLike, AxesLike]]=None,
) -> Array:
    """Create a physical array from a measured object.

    Parameters
    ----------
    x : `~measured.Object`
        The measured object from which to take numerical data and the associated
        metric unit. If `x` is a scalar object, this function will convert it to
        a 1-D object.
    axes : dimensions-like or axes-like
        Either an iterable of string dimensions (i.e., axis names) or a mapping
        from dimension to axis vector. The number of axes must equal the number
        of dimensions in `x`.

    Returns
    -------
    `~Array`

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

@typing.overload
def array(x: Array[real.ValueType], /) -> Array[real.ValueType]:
    """Create a physical array from an existing physical array."""

def array(*args, **kwargs):
    return _object_factories.array_factory(*args, **kwargs)


