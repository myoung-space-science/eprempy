"""
Support for real-valued numeric arrays.
"""

import numbers
import typing

import numpy
import numpy.typing

from .. import base
from .. import numeric
from ._types import ValueType


T = typing.TypeVar('T')


class Array(numeric.Array[T], base.abc.Real):
    """A concrete array-like object with named dimensions.

    This class provides a real-valued array-like interface to a variety of
    numeric objects by implementing the real-valued protocol for a generic
    array-like quantity.

    See Also
    --------
    `~array`
        The factory function for creating instances of this class.
    `~numeric.Array`
        The base class for generic array-like quantities.
    """

    __eq__ = numeric.implementation.binary('eq')
    __ne__ = numeric.implementation.binary('ne')
    __lt__ = numeric.implementation.binary('lt')
    __gt__ = numeric.implementation.binary('gt')
    __le__ = numeric.implementation.binary('le')
    __ge__ = numeric.implementation.binary('ge')

    __abs__ = numeric.implementation.unary('abs')
    __pos__ = numeric.implementation.unary('pos')
    __neg__ = numeric.implementation.unary('neg')

    __add__, __radd__ = numeric.implementation.doublet('add')
    __sub__, __rsub__ = numeric.implementation.doublet('sub')
    __mul__, __rmul__ = numeric.implementation.doublet('mul')
    __truediv__, __rtruediv__ = numeric.implementation.doublet('truediv')
    __floordiv__, __rfloordiv__ = numeric.implementation.doublet('floordiv')
    __mod__, __rmod__ = numeric.implementation.doublet('mod')
    __pow__, __rpow__ = numeric.implementation.doublet('pow')

    def _get_arg_data(self, arg):
        if isinstance(arg, Array):
            return self.array
        return super()._get_arg_data(arg)

    _FUNCTIONS = {}
    _OPERATORS = {}


Array._UFUNC_TYPES += [Array]
Array._FUNCTION_TYPES += [Array]


ArrayType = typing.TypeVar('ArrayType', bound=Array)


@Array.implements('eq')
def eq(a, b):
    """Compute a == b."""
    if isinstance(a, Array) and isinstance(b, Array):
        return (
            numpy.array_equal(a, b)
            and
            a.dimensions == b.dimensions
        )
    return False


@Array.implements('ne')
def ne(a, b):
    """Compute a != b."""
    return not (a == b)


@Array.implements('abs')
def abs(a):
    """Compute abs(a)."""
    return unary(numeric.operators.abs, a)


@Array.implements('pos')
def pos(a):
    """Compute +a."""
    return unary(numeric.operators.pos, a)


@Array.implements('neg')
def neg(a):
    """Compute -a."""
    return unary(numeric.operators.neg, a)


@Array.implements('round')
def round(a, /, ndigits: int=None):
    """Compute round(a[, ndigits])."""
    return unary(numeric.operators.round, a, ndigits=ndigits)


@Array.implements('lt')
def lt(a, b):
    """Compute a < b."""
    return comparative(numeric.operators.lt, a, b)


@Array.implements('le')
def le(a, b):
    """Compute a <= b."""
    return comparative(numeric.operators.le, a, b)


@Array.implements('gt')
def gt(a, b):
    """Compute a > b."""
    return comparative(numeric.operators.gt, a, b)


@Array.implements('ge')
def ge(a, b):
    """Compute a >= b."""
    return comparative(numeric.operators.ge, a, b)


@Array.implements('add')
def add(a, b):
    """Compute a + b."""
    try:
        result = additive(numeric.operators.add, a, b)
    except ValueError as err:
        raise ValueError("Cannot add arrays") from err
    return result


@Array.implements('sub')
def sub(a, b):
    """Compute a - b."""
    try:
        result = additive(numeric.operators.sub, a, b)
    except ValueError as err:
        raise ValueError("Cannot subtract arrays") from err
    return result


@Array.implements(numpy.multiply)
@Array.implements('mul')
def mul(a, b):
    """Compute a * b."""
    return multiplicative(numeric.operators.mul, a, b)


@Array.implements(numpy.true_divide)
@Array.implements('truediv')
def truediv(a, b):
    """Compute a / b."""
    return multiplicative(numeric.operators.truediv, a, b)


@Array.implements(numpy.floor_divide)
@Array.implements('floordiv')
def floordiv(a, b):
    """Compute a // b."""
    return multiplicative(numeric.operators.floordiv, a, b)


@Array.implements(numpy.mod)
@Array.implements('mod')
def mod(a, b):
    """Compute a % b."""
    return multiplicative(numeric.operators.mod, a, b)


@Array.implements(numpy.power)
@Array.implements('pow')
def pow(a, b, mod: int=None):
    """Compute a ** b."""
    if isinstance(a, Array) and isinstance(b, Array):
        if a.dimensions != b.dimensions:
            raise ValueError(
                "Cannot compute a ** b between two arrays"
                " with different dimensions"
            ) from None
    f = numeric.operators.pow
    if isinstance(a, (numbers.Number, numpy.ndarray)):
        return f(a, b.array)
    return multiplicative(f, a, b, mod=mod)


def unary(f, a, /):
    """Implement a unary arithmetic operation on array quantities."""
    if isinstance(a, Array):
        return array_factory(f(a.array), dimensions=a.dimensions)
    raise numeric.OperandTypeError(a)


def comparative(f, a, b, /):
    """Implement a comparative operation on array quantities."""
    if isinstance(a, Array) and isinstance(b, Array):
        if not a.dimensions == b.dimensions:
            raise ValueError(
                "Cannot compare arrays with different dimensions"
            ) from None
        return f(a.array, b.array)
    return f(a.array, b)


def additive(f, a, b, /):
    """Implement an additive operation on array quantities."""
    if isinstance(a, Array) and isinstance(b, Array):
        if not a.dimensions == b.dimensions:
            raise ValueError("Arrays have different dimensions") from None
        return array_factory(f(a.array, b.array), dimensions=a.dimensions)
    if isinstance(a, Array):
        return f(a.array, b)
    if isinstance(b, Array):
        return f(a, b.array)
    raise numeric.OperandTypeError(a, b)


def multiplicative(f, a, b, /, **kwargs):
    """Implement a multiplicative operation on array quantities."""
    try:
        operands = _get_operands(a, b)
    except TypeError as err:
        raise numeric.OperandTypeError(a, b) from err
    r = f(*operands, **kwargs)
    if isinstance(a, Array) and isinstance(b, Array):
        return array_factory(r, a.dimensions | b.dimensions)
    if isinstance(a, Array):
        return array_factory(r, a.dimensions)
    if isinstance(b, Array):
        return array_factory(r, b.dimensions)
    raise numeric.OperandTypeError(a, b)


def _get_operands(a, b):
    """Compute appropriate operands for a binary operation."""
    if isinstance(a, Array) and isinstance(b, Array):
        return numeric.remesh(a, b)
    return _get_operand(a), _get_operand(b)


def _get_operand(x):
    """Determine the appropriate operand for a mixed-type operation.
    
    This is a helper function for `_get_operands`. It assumes that
    `_get_operands` has already handled the case in which both arguments are
    data interfaces.
    """
    if isinstance(x, Array):
        return x.array
    if isinstance(x, numeric.Object):
        return x.data
    if isinstance(x, (numbers.Real, numpy.ndarray)):
        return x
    raise TypeError(x)


@Array.implements(numpy.array_equal)
def array_equal(
    a: Array[ValueType],
    b: Array[ValueType],
) -> bool:
    """Called for numpy.array_equal(a, b)."""
    return numpy.array_equal(numpy.array(a), numpy.array(b))


@Array.implements(numpy.squeeze)
def squeeze(x: Array[ValueType], **kwargs):
    """Called for numpy.squeeze(x)."""
    data = numpy.squeeze(x.array, **kwargs)
    if data.ndim == 0:
        return float(data)
    dimensions = [d for d, n in x.shapemap.items() if n != 1]
    return array_factory(data, dimensions=dimensions)


@Array.implements(numpy.mean)
def mean(x: Array[ValueType], **kwargs):
    """Compute the mean of the underlying array."""
    data = x.array.mean(**kwargs)
    axis = kwargs.get('axis')
    if axis is None:
        return data
    ax = axis % x.ndim
    dimensions = [d for d in x.dimensions if x.dimensions.index(d) != ax]
    return array_factory(data, dimensions=dimensions)


@Array.implements(numpy.sum)
def sum(x: Array[ValueType], **kwargs):
    """Compute the sum of the underlying array."""
    data = x.array.sum(**kwargs)
    axis = kwargs.get('axis')
    if axis is None:
        return data
    if 'keepdims' in kwargs:
        return array_factory(data, dimensions=x.dimensions)
    ax = x.ndim + axis if axis < 0 else axis
    dimensions = [d for d in x.dimensions if x.dimensions.index(d) != ax]
    return array_factory(data, dimensions=dimensions)


@Array.implements(numpy.cumsum)
def cumsum(x: Array[ValueType], **kwargs):
    """Compute the cumulative sum of the underlying array."""
    data = x.array.cumsum(**kwargs)
    if kwargs.get('axis') is None:
        return data
    return array_factory(data, dimensions=x.dimensions)


@Array.implements(numpy.transpose)
def transpose(x: Array[ValueType], **kwargs):
    """Compute the transpose of an array and dimensions."""
    data = x.array.transpose()
    axes = kwargs.get('axes')
    if axes is None:
        dimensions = x.dimensions[::-1]
        return array_factory(data, dimensions=dimensions)
    dimensions = [x.dimensions[i] for i in tuple(axes)]
    return array_factory(data, dimensions=dimensions)


@Array.implements(numpy.gradient)
def gradient(x: Array[ValueType], *args, **kwargs):
    """Compute the gradient of an array."""
    if not args:
        return _apply_gradient(x.dimensions, x.array, **kwargs)
    diffs = []
    for arg in args:
        if isinstance(arg, Array):
            diffs.append(arg.array)
        elif isinstance(arg, numbers.Real):
            diffs.append(float(arg))
        else:
            diffs.append(numpy.array(arg))
    return _apply_gradient(x.dimensions, x.array, *diffs, **kwargs)


def _apply_gradient(
    dimensions,
    *args,
    **kwargs
) -> typing.List[Array]:
    """Helper for `gradient`."""
    gradient = numpy.gradient(*args, **kwargs)
    if isinstance(gradient, list):
        return [
            array_factory(array, dimensions=dimensions)
            for array in gradient
        ]
    return array_factory(gradient, dimensions=dimensions)


@Array.implements(numpy.trapz)
def trapz(x: Array[ValueType], *args, **kwargs):
    """Integrate the array via the composite trapezoidal rule."""
    data = numpy.trapz(x.array, *args, **kwargs)
    axis = kwargs.get('axis')
    if axis is None:
        dimensions = x.dimensions[:-1]
    else:
        ax = axis % x.ndim
        dimensions = [d for d in x.dimensions if x.dimensions.index(d) != ax]
    return array_factory(data, dimensions=dimensions)


@typing.overload
def array_factory(*args, **kwargs) -> Array[T]:
    """Create an array from the given arguments, if possible."""

@typing.overload
def array_factory(x: T, /) -> Array[T]:
    """Create an array from `x`, with dimensions derived from `x`."""

@typing.overload
def array_factory(x: T, /, dimensions: typing.Iterable[str]) -> Array[T]:
    """Create an array from `x`, with the given dimensions."""

@typing.overload
def array_factory(x: T, *dimensions: str) -> Array[T]:
    """Create an array from `x`, with the given dimensions."""

@typing.overload
def array_factory(x: ArrayType, /) -> ArrayType:
    """Create an array from an existing array-like quantity."""

def array_factory(*args, **kwargs):
    return Array(*numeric._array.array_args(*args, **kwargs))


