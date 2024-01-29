"""
Support for working with indices of numeric arrays.
"""

import contextlib
import numbers
import typing

import numpy
import numpy.typing

from .. import container
from .. import exceptions
from .. import measurable
from ._data import isintegral
from ._mixins import Operators
from . import _implementation
from . import _operators
from . import _objects
from ._operations import OperandTypeError


T = typing.TypeVar('T')

I = typing.TypeVar('I', bound=typing.SupportsInt)


class Object(_objects.Object[T], Operators):
    """Base class for index objects."""

    __eq__ = _implementation.binary('eq')
    __ne__ = _implementation.binary('ne')
    __lt__ = _implementation.binary('lt')
    __gt__ = _implementation.binary('gt')
    __le__ = _implementation.binary('le')
    __ge__ = _implementation.binary('ge')

    __abs__ = _implementation.unary('abs')
    __pos__ = _implementation.unary('pos')
    __neg__ = _implementation.unary('neg')

    __add__, __radd__ = _implementation.doublet('add')
    __sub__, __rsub__ = _implementation.doublet('sub')
    __mul__, __rmul__ = _implementation.doublet('mul')
    __floordiv__, __rfloordiv__ = _implementation.doublet('floordiv')
    __mod__, __rmod__ = _implementation.doublet('mod')
    __pow__, __rpow__ = _implementation.doublet('pow')

    def _get_numpy_array(self):
        return numpy.array(self.data)

    _OPERATORS = {}
    _FUNCTIONS = {}


class Value(Object[int]):
    """An integral index value."""

    def __index__(self) -> int:
        """Called for use as an index or to convert to integer type."""
        return self.data

    def shift(self, __x: I, floor: I=None, ceil: I=None):
        """Shift index by a constant value."""
        index = int(self.data) + int(__x)
        if floor is not None and index < floor:
            return Value(floor)
        if ceil is not None and index > ceil:
            return Value(ceil)
        return Value(index)


ObjectType = typing.TypeVar('ObjectType', bound=Object)
"""Type variable bound to `~index.Object`."""


class Sequence(Object[numpy.typing.NDArray[numpy.integer]]):
    """A sequence of integral index values."""

    def __str__(self) -> str:
        if len(self.data) <= 4:
            return ', '.join(str(i) for i in self.data)
        indices = [*self.data[:2], '...', *self.data[-2:]]
        return ', '.join(str(i) for i in indices)

    # XXX: Should instances be iterators rather than iterables? See
    # https://stackoverflow.com/a/24377 for more information and suggestions.
    def __iter__(self):
        """Called for iter(self)."""
        yield from self.data

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.data)

    def __getitem__(self, __i: typing.SupportsIndex):
        """Called for self[i]."""
        data = self.data[__i]
        try:
            len(data)
        except TypeError:
            result = Value.spawn(data)
        else:
            result = self.spawn(data)
        return result

    def shift(self, __x: I, floor: I=None, ceil: I=None):
        """Shift indices by a constant value."""
        indices = numpy.array(self.data) + int(__x)
        if floor is not None:
            indices[indices < floor] = floor
        if ceil is not None:
            indices[indices > ceil] = ceil
        return Sequence(indices)


IndexType = typing.TypeVar('IndexType', Value, Sequence)

IndexLike = typing.Union[Value, Sequence]


def implements(operation):
    """Register `operation` as the implementation for all objects."""
    def wrapped(f):
        Value.implements(operation)(f)
        Sequence.implements(operation)(f)
        return f
    return wrapped


@implements('eq')
@exceptions.convert(OperandTypeError, False)
def eq(a, b, /):
    """Compute a == b."""
    return comparative(_operators.eq, a, b)


@implements('ne')
@exceptions.convert(OperandTypeError, True)
def ne(a, b, /):
    """Compute a != b."""
    return comparative(_operators.ne, a, b)


@implements('abs')
def abs(a):
    """Compute abs(a)."""
    return unary(_operators.abs, a)


@implements('pos')
def pos(a):
    """Compute +a."""
    return unary(_operators.pos, a)


@implements('neg')
def neg(a):
    """Compute -a."""
    return unary(_operators.neg, a)


@implements('round')
def round(a, /, ndigits: int=None):
    """Compute round(a[, ndigits])."""
    return unary(_operators.round, a, ndigits=ndigits)


@implements('lt')
@exceptions.convert(OperandTypeError, NotImplemented)
def lt(a, b):
    """Compute a < b."""
    return comparative(_operators.lt, a, b)


@implements('le')
@exceptions.convert(OperandTypeError, NotImplemented)
def le(a, b):
    """Compute a <= b."""
    return comparative(_operators.le, a, b)


@implements('gt')
@exceptions.convert(OperandTypeError, NotImplemented)
def gt(a, b):
    """Compute a > b."""
    return comparative(_operators.gt, a, b)


@implements('ge')
@exceptions.convert(OperandTypeError, NotImplemented)
def ge(a, b):
    """Compute a >= b."""
    return comparative(_operators.ge, a, b)


@implements('add')
def add(a, b):
    """Compute a + b."""
    return arithmetic(_operators.add, a, b)


@implements('sub')
def sub(a, b):
    """Compute a - b."""
    return arithmetic(_operators.sub, a, b)


@implements('mul')
def mul(a, b):
    """Compute a * b."""
    return arithmetic(_operators.mul, a, b)


@implements('floordiv')
def floordiv(a, b):
    """Compute a // b."""
    return arithmetic(_operators.floordiv, a, b)


@implements('mod')
def mod(a, b):
    """Compute a % b."""
    return arithmetic(_operators.mod, a, b)


@implements('pow')
def pow(a, b, mod: int=None):
    """Compute a ** b."""
    negative_exponent = False
    try:
        negative_exponent = b < 0
    except ValueError:
        negative_exponent = all(b < 0)
    if negative_exponent:
        raise ValueError(
            "Cannot raise index to a negative integral power"
        ) from None
    return arithmetic(_operators.pow, a, b, mod=mod)


A = typing.TypeVar('A', bound=numbers.Real)
R = typing.TypeVar('R', bound=numbers.Real)

def unary(
    f: typing.Callable[[A], R],
    a: IndexType,
    **kwargs
) -> IndexType:
    """Implement a unary operation on `Value` or `Sequence`."""
    if isinstance(a, Sequence):
        return a.spawn([f(v, **kwargs) for v in a])
    if isinstance(a, Value):
        return a.spawn(f(a.data, **kwargs))
    raise OperandTypeError(a)


B = typing.TypeVar('B', bound=numbers.Real)

BoolLike = typing.Union[bool, typing.Sequence[bool]]

def comparative(
    f: typing.Callable[[A, B], BoolLike],
    a: IndexType,
    b: IndexType,
) -> BoolLike:
    """Implement a binary comparative operation on `Value` or `Sequence`."""
    r = binary(f, a, b)
    if isinstance(a, Value) and isinstance(b, Value):
        return bool(r)
    return numpy.array(r, dtype=bool)


@typing.overload
def arithmetic(
    f: typing.Callable[[A, B], R],
    a: IndexType,
    b: Sequence,
    **kwargs
) -> Sequence: ...

@typing.overload
def arithmetic(
    f: typing.Callable[[A, B], R],
    a: Sequence,
    b: IndexType,
    **kwargs
) -> Sequence: ...

@typing.overload
def arithmetic(
    f: typing.Callable[[A, B], R],
    a: Value,
    b: Value,
    **kwargs
) -> Value: ...

@typing.overload
def arithmetic(
    f: typing.Callable[[A, B], R],
    a: typing.Union[IndexType, numbers.Real],
    b: typing.Union[IndexType, numbers.Real],
    **kwargs
) -> IndexType: ...

def arithmetic(f, a, b, **kwargs):
    """Implement a binary arithmetic operation on `Value` or `Sequence`."""
    r = binary(f, a, b, **kwargs)
    if isinstance(a, (Value, Sequence)) and isinstance(b, (Value, Sequence)):
        if all(isinstance(i, Value) for i in (a, b)):
            return _new_or_result(Value.spawn, r)
        return _new_or_result(Sequence.spawn, r)
    if isinstance(a, (Value, Sequence)) and isinstance(b, numbers.Integral):
        return _new_or_result(a.spawn, r)
    if isinstance(a, numbers.Integral) and isinstance(b, (Value, Sequence)):
        return _new_or_result(b.spawn, r)
    raise OperandTypeError(a, b)


def binary(f, a, b, **kwargs):
    """Compute f(a, b, **kwargs) on numeric data."""
    if isinstance(a, Sequence) and isinstance(b, Sequence):
        return [f(x, y, **kwargs) for (x, y) in zip(a.data, b.data)]
    if isinstance(a, Sequence):
        if isinstance(b, Value):
            return [f(x, b.data, **kwargs) for x in a.data]
        if isintegral(b):
            return [f(x, b, **kwargs) for x in a.data]
        raise OperandTypeError(a, b)
    if isinstance(b, Sequence):
        if isinstance(a, Value):
            return [f(a.data, y, **kwargs) for y in b.data]
        if isintegral(a):
            return [f(a, y, **kwargs) for y in b.data]
        raise OperandTypeError(a, b)
    if isinstance(a, Value) and isinstance(b, Value):
        return f(a.data, b.data, **kwargs)
    if isinstance(a, Value) and isintegral(b):
        return f(a.data, b, **kwargs)
    if isintegral(a) and isinstance(b, Value):
        return f(a, b.data, **kwargs)
    raise OperandTypeError(
        f"Expected operands to be instances of {Value} or {Sequence}"
    ) from None


def _new_or_result(factory, x):
    """Helper for computing correct return type.
    
    If applying `factory` to `x` succeeds, this function will return the result.
    Otherwise, it will return `x`.
    """
    try:
        result = factory(x)
    except Exception:
        result = x
    return result


@typing.overload
def value(
    x: typing.Union[
        typing.SupportsInt,
        typing.Iterable[typing.SupportsInt],
        numpy.typing.NDArray[numpy.integer],
    ],
    /,
) -> Value:
    """Create an index value from a numeric object.

    Parameters
    ----------
    x
        An object that supports conversion to `int`, an iterable object with a
        single member that supports conversion to `int`, or a one-element
        `numpy` array with integral data type.

    Returns
    -------
    `~Value`

    Raises
    ------
    `TypeError`
        The argument contains more than one element.
    """

@typing.overload
def value(x: measurable.Type, /) -> Value:
    """Create an index value from a unitless measurable object.

    Parameters
    ----------
    x
        An object with a `data` attribute and a unit equal to `'1'`.

    Returns
    -------
    `~Value`

    Raises
    -----
    `TypeError`
        The given object is not unitless.
    """

@Value.register.factory
def value(x, /):
    """Create a single numeric index value."""
    parsed = value_args(x)
    if isinstance(parsed, typing.SupportsInt):
        if isinstance(parsed, numpy.ndarray) and parsed.size == 1:
            return Value(int(parsed[0]))
        return Value(int(parsed))
    raise TypeError(
        f"Cannot convert {x} to a single integer"
    ) from None


@typing.overload
def sequence(
    x: typing.Union[
        typing.SupportsInt,
        typing.Iterable[typing.SupportsInt],
        numpy.typing.NDArray[numpy.integer],
    ],
    /,
) -> Sequence:
    """Create an index sequence from an iterable object with integer-like values.

    Parameters
    ----------
    x
        An object that supports conversion to `int`, an iterable object with
        members that all support conversion to `int`, or a `numpy` array with
        integral data type.

    Returns
    -------
    `~Value`

    Raises
    ------
    `TypeError`
        The given object cannot be coerced into a one-dimensional array.
    """

@typing.overload
def sequence(x: measurable.Type, /) -> Sequence:
    """Create an index sequence from a unitless measurable object.

    Parameters
    ----------
    x
        An object with a `data` attribute and a unit equal to `'1'`.

    Returns
    -------
    `~Value`

    Raises
    -----
    `TypeError`
        The given object is not unitless.
    """

@Sequence.register.factory
def sequence(x, /):
    """Create a sequence of numeric index values."""
    parsed = sequence_args(x)
    if all(isinstance(i, typing.SupportsInt) for i in parsed):
        return Sequence(numpy.array(parsed, dtype=int))
    raise TypeError(
        f"The numerical values of {x} do not all support"
        " conversion to integral type"
    ) from None


def value_args(x, /):
    """Parse arguments to initialize `~Value`."""
    index = _value_args(x)
    if index is not None:
        return index
    indices = _sequence_args(x)
    if indices is not None:
        return indices[0]
    raise TypeError(
        f"Cannot initialize {Value} from {x}, which has type {type(x)}"
    ) from None


def sequence_args(x, /):
    """Parse arguments to initialize `~Sequence`."""
    indices = _sequence_args(x)
    if indices is not None:
        return indices
    index = _value_args(x)
    if index is not None:
        return [index]
    raise TypeError(
        f"Cannot initialize {Sequence} from {x}, which has type {type(x)}"
    ) from None


def _value_args(x, /):
    """Helper for `index_args`."""
    if isinstance(x, numpy.ndarray) and x.dtype == int:
        if x.size == 1:
            v = x[0] if x.ndim == 1 else x
            return int(v)
        raise TypeError(
            f"Can only initialize {Value} from a"
            " zero- or one-dimensional array-like object"
        ) from None
    if isinstance(x, (numbers.Integral, numpy.integer)):
        return x
    if isinstance(x, (bytes, str)):
        try:
            index = int(x)
        except ValueError:
            return # Force a TypeError in factory
        return index
    if isinstance(x, measurable.Type):
        if x.isunitless:
            return x.data
        raise ValueError(
            f"Can only initialize {Value} from a unitless object"
        ) from None


def _sequence_args(x, /):
    """Helper for `indices_args`."""
    if isinstance(x, range):
        return x
    if isinstance(x, (tuple, list)):
        if all(isinstance(i, str) for i in x):
            with contextlib.suppress(ValueError):
                return [int(i) for i in x]
        if all(isinstance(i, (numbers.Integral, numpy.integer)) for i in x):
            return x
    if isinstance(x, numpy.ndarray) and x.dtype == int:
        if x.size == 1:
            v = x[0] if x.ndim == 1 else x
            return numpy.array(int(v), ndmin=1)
        y = x.squeeze()
        ndim = y.ndim
        if ndim == 1:
            return y
        raise TypeError(
            f"Cannot initialize {Sequence} from a {ndim}-D array"
        ) from None
    if isinstance(x, (numbers.Integral, numpy.integer)):
        return [x]
    if isinstance(x, Sequence):
        return x.data
    if isinstance(x, measurable.Type):
        if x.isunitless:
            return _sequence_args(x.data)
        raise ValueError(
            f"The argument to {Sequence} must be unitless."
        ) from None


_BUILTIN_TYPES = (int, slice, type(...), type(None))

_INDEX_DTYPES = (
    bool,
    numpy.int8,
    numpy.int16,
    numpy.int32,
    numpy.int64,
    numpy.uint8,
    numpy.uint16,
    numpy.uint32,
    numpy.uint64,
)

def resolve(shape: typing.Sequence[int], args):
    """Convert `args` into array indices based on `shape`.

    This function will first normalize `args` via `~normalize`. If the result
    contains an `Ellipsis` (i.e., `...`), this function will expand the
    `Ellipsis` via `~expand`. Otherwise, it will return the normalized indices.
    """
    normalized = normalize(shape, args)
    if _has_ellipsis(normalized):
        return expand(len(shape), normalized)
    return normalized


def _has_ellipsis(args):
    """Helper for `~resolve`."""
    try:
        iter(args)
    except TypeError:
        return False
    return any(arg is Ellipsis for arg in args)


def normalize(shape: typing.Sequence[int], args):
    """Compute appropriate array indices from `args`.

    If all indices in `args` have a standard form involving slices, an ellipsis,
    or integers, including 

    - `array[:]`
    - `array[...]`
    - `array[i, :]`
    - `array[:, j]`
    - `array[i, j]`

    (where i and j are integers) this function will immediately return them. If
    `args` is a `numpy.ndarray` with boolean type, this method will immediately
    return it. Otherwise, it will extract a sequence of indices that represents
    the original dimensions of the data.
    """
    if _normalized(args):
        return args
    if not isinstance(args, (tuple, list)):
        args = [args]
    expanded = expand_ellipsis(len(shape), *args)
    indices = []
    for i, arg in enumerate(expanded):
        if isinstance(arg, slice):
            indices.append(range(shape[i]))
        elif isintegral(arg):
            indices.append((arg,))
        else:
            indices.append(arg)
    return numpy.ix_(*list(indices))


def _normalized(args):
    """Helper for `~normalize`."""
    return (
        container.hastype(args, _BUILTIN_TYPES, tuple, strict=True)
        or
        isinstance(args, numpy.ndarray) and args.dtype in _INDEX_DTYPES
    )


def expand(ndim: int, indices):
    """Expand `indices` so that they will index `ndim` dimensions."""
    if isinstance(indices, (list, tuple)):
        return expand_ellipsis(ndim, *indices)
    if indices == slice(None):
        return expand_ellipsis(ndim, ...)
    if isinstance(indices, type(...)):
        return expand_ellipsis(ndim, indices)
    if ndim > 1:
        return expand_ellipsis(ndim, indices, ...)
    return (indices,)


def expand_ellipsis(ndim: int, *args: typing.SupportsIndex):
    """Expand an `Ellipsis` into one or more `slice` objects."""
    # If there are more arguments than dimensions, something is wrong. The one
    # exception is when the final argument is an Ellipsis. This allows upstream
    # code to programmatically use `...` to capture 0 or more remaining
    # dimensions. For example, `self.mfp[0, 0, ...]` should be equal to
    # `self.mfp[0, 0, :, :]` whereas `self.r[0, 0, ...]` should be equal to
    # `self.r[0, 0]`.
    nargs = len(args)
    if nargs > ndim and not isinstance(args[-1], type(...)):
        raise IndexError(
            f"Too many indices ({nargs}) for {ndim} dimensions"
        ) from None
    # Convert numpy arrays to lists to avoid ValueError in `count(...)`.
    norm = [
        list(arg) if isinstance(arg, numpy.ndarray) else arg
        for arg in args
    ]
    # Count the number of ellipses.
    count = norm.count(...)
    # If there is no ellipsis, there's nothing to do.
    if count == 0:
        return args
    # If there is more than one ellipsis, raise an exception.
    if count > 1:
        raise IndexError(
            f"Index arguments may only contain a single ellipsis ('...')"
        ) from None
    # Expand arguments into
    # 1) all arguments before the ellipsis
    # 2) a slice for every dimension represented by the ellipsis
    # 3) all arguments after the ellipsis
    nslice = ndim - nargs + 1
    ellpos = args.index(Ellipsis)
    return (
        *args[slice(0, ellpos)],
        *([slice(None)] * nslice),
        *args[slice(ellpos+1, nargs+1)],
    )


def restrict(
    array: numpy.ndarray,
    *targets: float,
    axis: typing.SupportsIndex,
) -> range:
    """Restrict indices of `array` around the target value(s) along `axis`.

    Parameters
    ----------
    array : array-like
        The array containing `target`.

    *targets : real
        The numerical value(s) in `array` whose index to bound. There must be at
        least one target value.

    axis : integral, default=-1
        The axis in `array` that contains the target value(s).

    Returns
    -------
    `range`

    Raises
    ------
    `ValueError`:
        The caller did not pass any target values.
    """
    if len(targets) == 0:
        raise ValueError("No target values to bound") from None
    if len(targets) == 1:
        lower, upper = _compute_bounds(array, targets[0], axis)
        return range(lower, upper+1)
    lower = None
    upper = None
    for target in targets:
        lo, hi = _compute_bounds(array, target, axis)
        lower = lo if lower is None else min(lower, lo)
        upper = hi if upper is None else max(upper, hi)
    return range(lower, upper+1)


def _compute_bounds(
    array: numpy.ndarray,
    target: float,
    axis: typing.SupportsIndex,
) -> typing.Tuple[int, int]:
    """Compute the indices in `array` that bound `target` along `axis`.

    This function is a helper for `~restrict`.
    """
    bounds = _get_index_bounds(array, target, axis=axis)
    if bounds.ndim == 1:
        size = bounds.size
        if size != 2:
            raise ValueError(
                f"Attempt to bound {target} along axis {axis} in {array}"
                f" produced a {size}-element array."
            ) from None
        return tuple(bounds)
    if bounds.ndim == 2:
        lower = numpy.min(bounds[:, 0])
        upper = numpy.max(bounds[:, 1])
        return lower, upper
    # NOTE: We can get `lower` and `upper` for N-D arrays by replacing `:` with
    # `...`. The problem is that they will be (N-1)-D arrays that we will then
    # need to split into individual index vectors before returning.
    raise NotImplementedError(
        f"Cannot compute bounds of {bounds.ndim}-D array"
    ) from None


def _get_index_bounds(
    array: numpy.typing.ArrayLike,
    target: numbers.Real,
    axis: typing.SupportsIndex=None,
) -> numpy.typing.NDArray[numpy.integer]:
    """Find the indices bounding the target value.

    This function is a helper for `~restrict`. It returns an array containing
    the indices bounding `target` at each slice along `axis`. The shape will be
    the same as that of `array` except for `axis`, which will be 2.
    """
    if axis is None:
        axis = -1
    return numpy.apply_along_axis(
        _find_1d_indices,
        int(axis),
        numpy.asfarray(array),
        float(target),
    )


def _find_1d_indices(
    array: numpy.ndarray,
    target: float,
) -> typing.Tuple[int, int]:
    """Find the bounding indices in a 1-D array."""
    leq = array <= target
    lower = numpy.where(leq)[0].max() if any(leq) else 0
    geq = array >= target
    upper = numpy.where(geq)[0].min() if any(geq) else len(array)-1
    return lower, upper


