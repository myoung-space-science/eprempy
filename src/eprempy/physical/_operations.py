import contextlib
import numbers
import typing

import numpy

from .. import etc
from ..measured import Object as Measured
from .. import numeric
from .. import quantity
from .. import real
from ._scalar import Scalar
from ._vector import Vector
from ._tensor import Tensor
from ._array import Array
from ._object_factories import (
    scalar_factory,
    vector_factory,
    tensor_factory,
    array_factory,
)
from ._exceptions import PhysicalTypeError


T = typing.TypeVar('T')


def objects(operation):
    """Register `operation` as the implementation for all physical objects."""
    def wrapped(f):
        Scalar.implements(operation)(f)
        Vector.implements(operation)(f)
        Tensor.implements(operation)(f)
        Array.implements(operation)(f)
        return f
    return wrapped


@objects('eq')
def eq(a, b, /):
    """Compute a == b."""
    if isinstance(a, Measured) and isinstance(b, Measured):
        base = numeric.data.isequal(a.data, b.data) and a.unit == b.unit
        if isinstance(a, Array) and isinstance(b, Array):
            return base and a.axes == b.axes
        return base
    return False


@objects('ne')
def ne(a, b, /):
    """Compute a != b."""
    return not eq(a, b)


@objects('lt')
def lt(a, b, /):
    """Compute a < b."""
    return comparative(numeric.operators.lt, a, b)


@objects('le')
def le(a, b, /):
    """Compute a <= b."""
    return comparative(numeric.operators.le, a, b)


@objects('gt')
def gt(a, b, /):
    """Compute a > b."""
    return comparative(numeric.operators.gt, a, b)


@objects('ge')
def ge(a, b, /):
    """Compute a >= b."""
    return comparative(numeric.operators.ge, a, b)


@objects('abs')
def abs(a, /):
    """Compute abs(a)."""
    return unary(numeric.operators.abs, a)


@objects('pos')
def pos(a, /):
    """Compute +a."""
    return unary(numeric.operators.pos, a)


@objects('neg')
def neg(a, /):
    """Compute -a."""
    return unary(numeric.operators.neg, a)


@objects('add')
def add(a, b, /):
    """Compute a + b."""
    return additive(numeric.operators.add, a, b)


@objects('sub')
def sub(a, b, /):
    """Compute a - b."""
    return additive(numeric.operators.sub, a, b)


@objects('mul')
def mul(a, b, /):
    """Compute a * b."""
    return multiplicative(numeric.operators.mul, a, b)


@objects('truediv')
def truediv(a, b, /):
    """Compute a / b."""
    return multiplicative(numeric.operators.truediv, a, b)


@objects('floordiv')
def floordiv(a, b, /):
    """Compute a // b."""
    return multiplicative(numeric.operators.floordiv, a, b)


@objects('mod')
def mod(a, b, /):
    """Compute a % b."""
    return multiplicative(numeric.operators.mod, a, b)


@objects('pow')
def pow(a, b, mod: int=None):
    """Compute a ** b."""
    return exponential(numeric.operators.pow, a, b, mod=mod)


@Scalar.implements('round')
def round(a, /, ndigits: int=None):
    """Compute round(a[, ndigits])."""
    return unary(numeric.operators.round, a, ndigits=ndigits)


@Scalar.implements('floor')
def floor(a, /):
    """Compute floor(a)."""
    return unary(numeric.operators.floor, a)


@Scalar.implements('ceil')
def ceil(a, /):
    """Compute ceil(a)."""
    return unary(numeric.operators.ceil, a)


@Scalar.implements('trunc')
def trunc(a, /):
    """Compute trunc(a)."""
    return unary(numeric.operators.trunc, a)


@Scalar.implements('int')
def asint(a):
    """Compute int(self)."""
    return cast(int, a, typing.SupportsInt)


@Scalar.implements('float')
def asfloat(a):
    """Compute float(self)."""
    return cast(float, a, typing.SupportsFloat)


@Scalar.implements('complex')
def ascomplex(a):
    """Compute complex(self)."""
    return cast(complex, a, typing.SupportsComplex)


def cast(__type: T, a, protocol: typing.Optional[type]=None) -> T:
    """Convert `a` to `__type`, if possible."""
    if isinstance(a, Measured):
        if protocol and isinstance(a.data, protocol):
            return __type(a.data)
    raise PhysicalTypeError(
        f"Cannot convert {a} to {__type!r}"
    ) from None


def comparative(f: typing.Callable[..., T], a, b, /):
    """Compute a comparative binary operation."""
    if isinstance(a, Measured) and isinstance(b, Measured):
        if a.unit == b.unit:
            return f(a.data, b.data)
        raise ValueError(
            f"Cannot apply {f.__name__!r}"
            " to objects with different units."
        ) from None
    if isinstance(a, Measured) and isinstance(b, numbers.Real):
        return f(a.data, b)
    if isinstance(a, numbers.Real) and isinstance(b, Measured):
        return f(a, b.data)
    raise PhysicalTypeError(a)


def from_builtin(operation):
    """Process the result of a built-in operation."""
    def wrapped(f, *args, **kwargs):
        result = operation(f, *args, **kwargs)
        if isinstance(result, numeric.Result):
            return result.apply(_get_factory(*args))
        return result
    return wrapped


def from_numpy(operation):
    """Process the result of a numpy operation."""
    def wrapped(*args, **kwargs):
        result = operation(*args, **kwargs)
        factory = _get_factory(*args)
        if isinstance(result, numeric.Result):
            return result.apply(factory)
        if isinstance(result, (list, tuple)):
            converted = [
                x.apply(factory) if isinstance(x, numeric.Result) else x
                for x in result
            ]
            if isinstance(result, tuple):
                return tuple(converted)
            return converted
        return result
    return wrapped


def _get_factory(*operands):
    """Get the appropriate factory for creating a new object."""
    if any(isinstance(operand, Array) for operand in operands):
        return array_factory
    if any(isinstance(operand, Tensor) for operand in operands):
        return tensor_factory
    if any(isinstance(operand, Vector) for operand in operands):
        return vector_factory
    if any(isinstance(operand, Scalar) for operand in operands):
        return scalar_factory
    raise TypeError(
        f"Cannot determine appropriate factory from {operands}"
    ) from None


@from_builtin
def unary(f, a, /, **kwargs):
    """Compute a unary arithmetic operation."""
    if isinstance(a, Measured):
        try:
            unit = f(a.unit)
        except TypeError:
            unit = a.unit
        metadata = {'unit': unit}
        if isinstance(a, Array):
            metadata['axes'] = a.axes
        return numeric.Result(f(a.data, **kwargs), **metadata)
    raise PhysicalTypeError(a)


@from_builtin
def additive(f, a, b, /):
    """Compute an additive binary operation."""
    if isinstance(a, Measured):
        if a.unit != '1' and isinstance(b, (numbers.Number, numpy.number)):
            raise PhysicalTypeError(a, b)
    if isinstance(b, Measured):
        if b.unit != '1' and isinstance(a, (numbers.Number, numpy.number)):
            raise PhysicalTypeError(a, b)
    x = a if isinstance(a, Measured) else quantity.measure(a)
    y = b if isinstance(b, Measured) else quantity.measure(b)
    if not (isinstance(x, Measured) and isinstance(y, Measured)):
        raise PhysicalTypeError(x, y)
    opr = numeric.CALLABLES.find(f)
    msg = "Cannot {} objects with different {}."
    if isinstance(x, Array) and isinstance(y, Array):
        data = f(x.data, y.data)
        badattrs = []
        if x.unit == y.unit:
            if x.axes == y.axes:
                return array_factory(data, unit=x.unit, axes=x.axes)
            with contextlib.suppress(ValueError):
                axes = x.axes + y.axes
                return array_factory(data, unit=x.unit, axes=axes)
        if x.unit != y.unit:
            badattrs.append('units')
        if x.axes != y.axes:
            badattrs.append('bases')
        raise ValueError(msg.format(opr, etc.join(badattrs)))
    if isinstance(x, Array):
        if isinstance(y, Vector):
            raise TypeError(
                f"Cannot {opr} a vector to an array"
            ) from None
        data = f(x.data.array, y.data)
        if x.unit == y.unit:
            return array_factory(data, unit=x.unit, axes=x.axes)
        raise ValueError(msg.format(opr, 'units'))
    if isinstance(y, Array):
        if isinstance(x, Vector):
            raise TypeError(
                f"Cannot {opr} a vector to an array"
            ) from None
        data = f(x.data, y.data.array)
        if x.unit == y.unit:
            return array_factory(data, unit=x.unit, axes=y.axes)
        raise ValueError(msg.format(opr, 'units'))
    data = f(x.data, y.data)
    if x.unit == y.unit:
        return numeric.Result(data, unit=x.unit)
    raise ValueError(msg.format(opr, 'units'))


@from_builtin
def multiplicative(f, a, b):
    """Compute a multiplicative binary operation."""
    g = f if f == numeric.operators.mul else numeric.operators.truediv
    if isinstance(a, Measured) and isinstance(b, Measured):
        unit = g(a.unit, b.unit)
        if isinstance(a, Array) and isinstance(b, Array):
            data = f(a.data, b.data)
            axes = a.axes | b.axes
            return array_factory(data, unit=unit, axes=axes)
        if isinstance(a, Array):
            data = f(a.data.array, b.data)
            axes = a.axes
            return array_factory(data, unit=unit, axes=axes)
        if isinstance(b, Array):
            data = f(a.data, b.data.array)
            axes = b.axes
            return array_factory(data, unit=unit, axes=axes)
        return numeric.Result(f(a.data, b.data), unit=unit)
    if isinstance(a, Measured) and isinstance(b, numbers.Real):
        # If `b == 1`, both `a.unit * b` and `a.unit / b` will return `a.unit`.
        # If `b != 1`, neither `a.unit * b` nor `a.unit / b` is defined.
        # Therefore, we just set the new unit to `a.unit`.
        unit = a.unit
        if isinstance(a, Array):
            data = f(a.data.array, b)
            axes = a.axes
            return array_factory(data, unit=unit, axes=axes)
        return numeric.Result(f(a.data, b), unit=unit)
    if isinstance(a, numbers.Real) and isinstance(b, Measured):
        # We only want the unit or its inverse, depending on the operation,
        # regardless of the numerical value of `b`.
        unit = g(1, b.unit)
        if isinstance(b, Array):
            data = f(a, b.data.array)
            axes = b.axes
            return array_factory(data, unit=unit, axes=axes)
        return numeric.Result(f(a, b.data), unit=unit)
    x = a if isinstance(a, Measured) else quantity.measure(a)
    y = b if isinstance(b, Measured) else quantity.measure(b)
    if not (isinstance(x, Measured) and isinstance(y, Measured)):
        raise PhysicalTypeError(x, y)
    return multiplicative(f, x, y)


@from_builtin
def exponential(f, a, b, **kwargs):
    """Compute an exponential binary operation."""
    if isinstance(b, Measured) and not b.isunitless:
        raise ValueError(
            "Cannot compute a ** b unless b is unitless"
        ) from None
    if isinstance(a, Measured) and isinstance(b, Measured):
        if isinstance(b, Scalar):
            p = b.data
            unit = f(a.unit, p)
            if isinstance(a, Array):
                data = f(a.data.array, p, **kwargs)
                return array_factory(data, unit=unit, axes=a.axes)
            return numeric.Result(f(a.data, p, **kwargs), unit=unit)
        if not a.isunitless:
            raise ValueError(
                "Cannot compute a ** b when b is array-like"
                " unless both a and b are unitless"
            )
        # At this point, we know:
        # - both `a` and `b` are unitless
        # - `b` is array-like
        if isinstance(a, Array) and isinstance(b, Array):
            data = f(a.data.array, b.data.array, **kwargs)
            return array_factory(data, unit='1', axes=a.axes)
        if isinstance(a, Array):
            data = f(a.data.array, b.data, **kwargs)
            return array_factory(data, unit='1', axes=a.axes)
        if isinstance(b, Array):
            data = f(a.data, b.data.array, **kwargs)
            return array_factory(data, unit='1', axes=b.axes)
        return numeric.Result(f(a.data, b.data, **kwargs), unit='1')
    if isinstance(a, Measured) and isinstance(b, numbers.Real):
        unit = f(a.unit, b)
        if isinstance(a, Array):
            data = f(a.data.array, b, **kwargs)
            return array_factory(data, unit=unit, axes=a.axes)
        return numeric.Result(f(a.data, b, **kwargs), unit=unit)
    if isinstance(a, (numbers.Real, numpy.ndarray)) and isinstance(b, Measured):
        if isinstance(b, Array):
            return f(a, b.data.array, **kwargs)
        return f(a, b.data, **kwargs)
    raise PhysicalTypeError(a, b)


@from_numpy
@Tensor.implements(numpy.power)
@Vector.implements(numpy.power)
@Array.implements(numpy.power)
def power(a, b, **kwargs):
    """Called for numpy.power(a, b)."""
    if isinstance(b, (Vector, Tensor, Array)) and not b.isunitless:
        raise ValueError(
            "Cannot compute a ** b unless b is unitless"
        ) from None
    x = a.data if isinstance(a, Measured) else a
    y = b.data if isinstance(b, Measured) else b
    return numpy.power(x, y, **kwargs)


@objects(numpy.array_equal)
def array_equal(
    x: Measured[real.ValueType],
    y: Measured[real.ValueType],
) -> bool:
    return numpy.array_equal(numpy.array(x), numpy.array(y))


@objects(numpy.sin)
@from_numpy
def sin(x: Measured[real.ValueType]):
    """Compute the sin of `x`."""
    return _apply_trig(numpy.sin, x)


@objects(numpy.cos)
@from_numpy
def cos(x: Measured[real.ValueType]):
    """Compute the cosine of `x`."""
    return _apply_trig(numpy.cos, x)


@objects(numpy.tan)
@from_numpy
def tan(x: Measured[real.ValueType]):
    """Compute the tangent of `x`."""
    return _apply_trig(numpy.tan, x)


def _apply_trig(f, x: Measured[real.ValueType]):
    """Compute a trigonometric function of `x`."""
    if str(x.unit) in {'rad', 'deg'}:
        metadata = {'unit': '1'}
        if isinstance(x, Array):
            metadata['axes'] = x.axes
        return numeric.Result(f(x.data), **metadata)
    strf = f.__name__
    raise ValueError(
        f"Cannot compute {strf}(x)"
        f" when the unit of x is {str(x.unit)!r}"
    ) from None


@objects(numpy.sqrt)
@from_numpy
def sqrt(x: Measured[real.ValueType]):
    """Compute the square root of `x`."""
    data = numpy.sqrt(x.data)
    metadata = {'unit': x.unit ** 0.5}
    if isinstance(x, Array):
        metadata['axes'] = x.axes
    return numeric.Result(data, **metadata)


@objects(numpy.log)
@from_numpy
def log(x: Measured[real.ValueType]):
    """Compute the natural log of `x`."""
    return _apply_log(numpy.log, x)


@objects(numpy.log10)
@from_numpy
def log10(x: Measured[real.ValueType]):
    """Compute the base-10 log of `x`."""
    return _apply_log(numpy.log10, x)


@objects(numpy.log2)
@from_numpy
def log2(x: Measured[real.ValueType]):
    """Compute the base-2 log of `x`."""
    return _apply_log(numpy.log2, x)


@objects(numpy.log1p)
@from_numpy
def log1p(x: Measured[real.ValueType]):
    """Compute the natural log of `x + 1`."""
    return _apply_log(numpy.log1p, x)


def _apply_log(f, x: Measured[real.ValueType]):
    """Compute a logarithmic function of `x`."""
    if str(x.unit) == '1':
        metadata = {'unit': '1'}
        if isinstance(x, Array):
            metadata['axes'] = x.axes
        return numeric.Result(f(x.data), **metadata)
    strf = f.__name__
    raise ValueError(
        f"Cannot compute {strf}(x) when x is not unitless"
    ) from None


@objects(numpy.squeeze)
@from_numpy
def squeeze(x: Measured[real.ValueType], **kwargs):
    """Remove singular axes.

    Notes
    -----
    - Returning a scalar from a singular array is consistent with applying
      `numpy.squeeze` to a singular `numpy.ndarray`. For example,

      >>> numpy.squeeze(numpy.array([2])).ndim
      0
    """
    if isinstance(x, Scalar):
        return x
    data = numpy.squeeze(x.data, **kwargs)
    if isinstance(data, (numbers.Real)):
        return scalar_factory(data, unit=x.unit)
    if isinstance(data, numpy.ndarray) and data.ndim == 0:
        return scalar_factory(numpy.ravel(data)[0], unit=x.unit)
    metadata = {'unit': x.unit}
    if isinstance(x, Array):
        metadata['axes'] = {d: x.axes[d] for d in data.dimensions}
    return numeric.Result(data, **metadata)


@objects(numpy.min)
@from_numpy
def npmin(x: Measured[real.ValueType], **kwargs):
    """Compute the minimum value of `x`."""
    data = numpy.min(x.data, **kwargs)
    if isinstance(x, Scalar) or 'axis' not in kwargs:
        return scalar_factory(data, unit=x.unit)
    metadata = {'unit': x.unit}
    if isinstance(x, Array):
        metadata['axes'] = {d: x.axes[d] for d in data.dimensions}
    return numeric.Result(data, **metadata)


@objects(numpy.max)
@from_numpy
def npmax(x: Measured[real.ValueType], **kwargs):
    """Compute the maximum value of `x`."""
    data = numpy.max(x.data, **kwargs)
    if isinstance(x, Scalar) or 'axis' not in kwargs:
        return scalar_factory(data, unit=x.unit)
    metadata = {'unit': x.unit}
    if isinstance(x, Array):
        metadata['axes'] = {d: x.axes[d] for d in data.dimensions}
    return numeric.Result(data, **metadata)


@objects(numpy.mean)
@from_numpy
def mean(x: Measured[real.ValueType], **kwargs):
    """Compute the mean of `x`."""
    data = numpy.mean(x.data, **kwargs)
    if isinstance(x, Scalar) or 'axis' not in kwargs:
        return scalar_factory(data, unit=x.unit)
    metadata = {'unit': x.unit}
    if isinstance(x, Array):
        metadata['axes'] = {d: x.axes[d] for d in data.dimensions}
    return numeric.Result(data, **metadata)


@objects(numpy.sum)
@from_numpy
def sum(x: Measured[real.ValueType], **kwargs):
    """Compute the sum of `x`."""
    data = numpy.sum(x.data, **kwargs)
    if isinstance(x, Scalar) or 'axis' not in kwargs:
        return scalar_factory(data, unit=x.unit)
    metadata = {'unit': x.unit}
    if isinstance(x, Array):
        metadata['axes'] = {d: x.axes[d] for d in data.dimensions}
    return numeric.Result(data, **metadata)


@objects(numpy.cumsum)
@from_numpy
def cumsum(x: Measured[real.ValueType], **kwargs):
    """Compute the cumulative sum of `x`.

    Notes
    -----
    - Calling plain `numpy.cumsum` on a number, on a 1-D array, and without
      passing an argument to `axis` all produces a 1-D array. Calling the same
      function on an N-D array (N >= 1) and including an argument to `axis`
      produces an N-D array. That is why calling this implementation on a
      scalar, on a vector, and without passing an argument to `axis` produces a
      vector whereas calling it on a vector, tensor, or array and including an
      argument to `axis` produces an instance of the same object. Note that
      calling this implementation with `axis=0` or `axis=-1` on a scalar will
      produce a vector and doing so with any argument to `axis` will raise an
      exception. This behavior is also consistent with the plain `numpy.cumsum`
      implementation.
    """
    data = numpy.cumsum(x.data, **kwargs)
    if isinstance(x, (Scalar, Vector)) or 'axis' not in kwargs:
        return vector_factory(data, unit=x.unit)
    metadata = {'unit': x.unit}
    if isinstance(x, Array):
        metadata['axes'] = {d: x.axes[d] for d in data.dimensions}
    return numeric.Result(data, **metadata)


@objects(numpy.transpose)
@from_numpy
def transpose(x: Measured[real.ValueType], **kwargs):
    """Compute the transpose of `x`."""
    data = numpy.transpose(x.data, **kwargs)
    if isinstance(x, Scalar):
        return scalar_factory(numpy.ravel(data)[0], unit=x.unit)
    metadata = {'unit': x.unit}
    if isinstance(x, Array):
        metadata['axes'] = {d: x.axes[d] for d in data.dimensions}
    return numeric.Result(data, **metadata)


@objects(numpy.gradient)
@from_numpy
def gradient(x: Measured[real.ValueType], *args, **kwargs):
    """Compute the gradient of an array."""
    if isinstance(x, Scalar):
        return []
    if not args:
        return _apply_gradient(x.unit, x, **kwargs)
    diffs = []
    units = []
    for arg in args:
        if isinstance(arg, Scalar):
            diffs.append(float(arg))
            units.append(arg.unit)
        elif isinstance(arg, (Vector, Tensor, Array)):
            diffs.append(numpy.array(arg))
            units.append(arg.unit)
        elif isinstance(arg, numbers.Real):
            diffs.append(float(arg))
            units.append('1')
        else:
            diffs.append(numpy.array(arg))
            units.append('1')
    u0 = units[0]
    if all(unit == u0 for unit in units[1:]):
        return _apply_gradient(x.unit / u0, x, *diffs, **kwargs)
    raise TypeError("Inconsistent units in gradient coordinates") from None


def _apply_gradient(unit, x, *args, **kwargs):
    """Helper for custom implementation of `numpy.gradient`."""
    gradient = numpy.gradient(numpy.array(x), *args, **kwargs)
    metadata = {'unit': unit}
    if isinstance(x, Array):
        metadata['axes'] = x.axes
    if isinstance(gradient, list):
        return [numeric.Result(array, **metadata) for array in gradient]
    return numeric.Result(gradient, **metadata)


@Array.implements(numpy.trapz)
@from_numpy
def trapz(x: Measured[real.ValueType], *args, **kwargs):
    """Integrate `x` via the composite trapezoidal rule."""
    if isinstance(x, Scalar):
        raise TypeError(
            "Cannot apply numpy.trapz to a scalar object"
        ) from None
    data = numpy.trapz(x.data, *args, **kwargs)
    if isinstance(data, (numbers.Real, numpy.number)):
        return data
    metadata = {'unit': x.unit}
    if isinstance(x, Array):
        metadata['axes'] = {d: x.axes[d] for d in data.dimensions}
    return numeric.Result(data, **metadata)


