import collections.abc
import contextlib
import numbers
import typing

import numpy
import numpy.typing

from .. import base
from .. import container
from .. import etc
from . import _data
from . import _index
from . import _operators
from ..typehelp import Self
from ._objects import (
    Object,
    Quantity,
)
from ._mixins import Operators


T = typing.TypeVar('T')


class DimensionTypeError(Exception):
    """Invalid type for operation on dimensions."""


@etc.autostr
class Dimensions(collections.abc.Sequence):
    """A representation of one or more array-axis names.
    
    This class is formally a sequence but it supports certain set-like
    operations in an order-preserving way.
    """

    def __init__(self, names: typing.Tuple[str]) -> None:
        self._names = names

    def __eq__(self, other):
        """Called for self == other."""
        if isinstance(other, Dimensions):
            return self._names == other._names
        if isinstance(other, str) and len(self) == 1:
            return self._names[0] == other
        try:
            truth = self._names == tuple(other)
        except TypeError:
            return False
        return truth

    def __lt__(self, other):
        """Called for self < other."""
        return self._compare(other, _operators.lt)

    def __le__(self, other):
        """Called for self <= other."""
        return self._compare(other, _operators.le)

    def __gt__(self, other):
        """Called for self > other."""
        return self._compare(other, _operators.gt)

    def __ge__(self, other):
        """Called for self >= other."""
        return self._compare(other, _operators.ge)

    def _compare(self, other, operator: typing.Callable[..., T]) -> T:
        """Implement a binary comparison between this instance and `other`."""
        these = set(self._names)
        those = set(other._names if isinstance(other, Dimensions) else other)
        return operator(these, those)

    def replace(self, old: str, new: str):
        """Replace a single dimension."""
        return dimensions_factory(
            *[new if n == old else n for n in self._names]
        )

    def insert(self, name: str, index: typing.SupportsIndex=None):
        """Insert the named dimension at `index`."""
        names = list(self._names)
        if index is not None:
            names.insert(index, name)
        else:
            names.append(name)
        return dimensions_factory(*names)

    def __and__(self, other):
        """Called for self & other."""
        try:
            those = self._get_operand(other)
        except DimensionTypeError:
            return NotImplemented
        full = list(self._names) + those
        common = set(self._names) & set(those)
        return dimensions_factory(*[n for n in full if n in common])

    def __rand__(self, other):
        """Called for other & self."""
        try:
            those = self._get_operand(other)
        except DimensionTypeError:
            return NotImplemented
        full = those + list(self._names)
        common = set(self._names) & set(those)
        return dimensions_factory(*[n for n in full if n in common])

    def __sub__(self, other):
        """Called for self - other."""
        try:
            those = self._get_operand(other)
        except DimensionTypeError:
            return NotImplemented
        return dimensions_factory(*[n for n in self if n not in those])

    def __rsub__(self, other):
        """Called for other - self."""
        if isinstance(other, Dimensions):
            return dimensions_factory(*[n for n in other if n not in self])
        raise NotImplemented

    def __or__(self, other):
        """Called for self | other."""
        try:
            those = self._get_operand(other)
        except DimensionTypeError:
            return NotImplemented
        these = list(self._names)
        try:
            merged = container.merge(these, those)
        except container.MergeError as err:
            errmsg = str(err).replace('entries', 'dimensions')
            raise ValueError(errmsg) from err
        return dimensions_factory(merged)

    def __ror__(self, other):
        """Called for other | self."""
        try:
            those = self._get_operand(other)
        except DimensionTypeError:
            return NotImplemented
        these = list(self._names)
        try:
            merged = container.merge(those, these)
        except container.MergeError as err:
            errmsg = str(err).replace('entries', 'dimensions')
            raise ValueError(errmsg) from err
        return dimensions_factory(merged)

    def __xor__(self, other):
        """Called for self ^ other."""
        try:
            those = self._get_operand(other)
        except DimensionTypeError:
            return NotImplemented
        return (self - those) | (those - self)

    def __rxor__(self, other):
        """Called for other ^ self."""
        try:
            those = self._get_operand(other)
        except DimensionTypeError:
            return NotImplemented
        return (those - self) | (self - those)

    def _get_operand(self, arg) -> typing.List[str]:
        """Return an appropriate operand for binary operations."""
        if isinstance(arg, Dimensions):
            return list(arg._names)
        if isinstance(arg, str):
            return [arg]
        try:
            iter(arg)
        except TypeError:
            raise DimensionTypeError(arg)
        if all(isinstance(i, str) for i in arg):
            return list(arg)
        raise DimensionTypeError(arg)

    def copy(self):
        """Create a copy of this instance."""
        return dimensions_factory(*self._names)

    @typing.overload
    def permute(
        self,
        order: typing.Iterable[typing.SupportsIndex],
    ) -> Self: ...

    @typing.overload
    def permute(self, *order: typing.SupportsIndex) -> Self: ...

    def permute(self, *args, **kwargs):
        """Reorder these dimensions."""
        if args and 'order' in kwargs:
            raise TypeError("Too many arguments") from None
        if args:
            if len(args) == 1:
                return self._permute(args[0])
            return self._permute(args)
        if 'order' in kwargs:
            return self._permute(kwargs['order'])
        raise TypeError("No arguments") from None

    def _permute(self, axes: typing.Iterable[typing.SupportsIndex]):
        """Helper for `~permute`."""
        try:
            names = [self[axis] for axis in axes]
        except (IndexError, TypeError) as err:
            raise ValueError(
                "Cannot interpret all values as indices"
            ) from err
        self.mismatch(names)
        return dimensions_factory(names)

    def mismatch(self, other: typing.Iterable[str]):
        """Raise an exception if `self < other` or `self > other`.

        This is a convenience method to checking whether `self == other` in a
        set-wise sense, and issuing a descriptive message depending upon whether
        `self` is a subset of `other` or vice versa. Note that it can also be
        used as a static method to compare two iterables of strings.

        Parameters
        ----------
        other : iterable of strings
            The object to compare to this collection (or to the first argument,
            when called as a static method).

        Returns
        -------
        `None`
            The two collections are equal in a set-wise sense.

        Raises
        ------
        `ValueError`
            The two collections are unequal in a set-wise sense.
        """
        a = set(self)
        b = set(other)
        if a < b:
            raise ValueError("Not enough dimensions") from None
        if a > b:
            diff = a - b
            dims = etc.join(diff, 'or', quoted=True)
            raise ValueError(
                f"Original dimensions do not include {dims}"
            ) from None

    def __hash__(self):
        """Support use as a mapping key."""
        return hash(self._names)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self._names)

    def __getitem__(self, __i: typing.SupportsIndex):
        """Called for index-based access."""
        return self._names[__i]

    def __str__(self) -> str:
        return f"{{{', '.join(repr(name) for name in self._names)}}}"


@typing.overload
def dimensions_factory(*args) -> Dimensions:
    """Create array dimensions from the given arguments, if possible."""

@typing.overload
def dimensions_factory(names: typing.Iterable[str]) -> Dimensions:
    """Create array dimensions from an iterable of names."""

@typing.overload
def dimensions_factory(*names: str) -> Dimensions:
    """Create array dimensions from one or more names."""

@typing.overload
def dimensions_factory(n: int) -> Dimensions:
    """Create `n` array dimensions with default names."""

def dimensions_factory(*args):
    """Factory function for data dimensions."""
    if len(args) == 1:
        arg = args[0]
        if isinstance(arg, numbers.Real):
            return tuple(f'x{i}' for i in range(arg))
    unwrapped = container.unwrap(args, newtype=tuple)
    unique = container.unique(unwrapped)
    return Dimensions(_compute_names(unique))


def _compute_names(args: typing.Iterable[str]) -> typing.Tuple[str]:
    """Determine the instance names from arguments."""
    if isinstance(args, Dimensions):
        return args._names
    if all(isinstance(arg, str) for arg in args):
        return tuple(args)
    raise TypeError(
        f"Unable to compute dimension names from {args!r}"
    ) from None


IndexLike = typing.Union[
    typing.SupportsIndex,
    typing.Tuple[typing.SupportsIndex],
    slice,
]

ArrayLike = typing.Union[base.Array, numpy.typing.NDArray]

DataType = typing.TypeVar('DataType', base.Array, numpy.ndarray)


class Array(Quantity[DataType], Operators):
    """Base class for numeric arrays with named dimensions."""

    def __init__(
        self,
        data: DataType,
        dimensions: Dimensions,
    ) -> None:
        super().__init__(data)
        self._shape = data.shape
        self._size = data.size
        self._ndim = data.ndim
        self._dimensions = dimensions
        self._array = data if isinstance(data, numpy.ndarray) else None

    def __eq__(self, other):
        """Called for self == other."""
        if isinstance(other, Array):
            return (
                numpy.array_equal(self.array, other.array)
                and
                self.dimensions == other.dimensions
            )
        return False

    def __ne__(self, other):
        """Called for self != other."""
        return not (self == other)

    def __contains__(self, __x) -> bool:
        """Called for x in self.
        
        See Also
        --------
        array_contains
            Perform additional containment checks beyond this method.
        """
        return __x in self._object or __x in self.array

    def __iter__(self):
        """Called for iter(self)."""
        return iter(self._object)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self._object)

    def __getitem__(self, args: IndexLike):
        """Called for subscription."""
        x = [args] if isinstance(args, typing.SupportsIndex) else args
        return self.spawn(
            self._getitem(x),
            dimensions=self.dimensions,
        )

    def _getitem(self, args):
        """Extract a subarray.

        This method exists independently of `__getitem__` in order to separate
        the subscription logic from the return-type logic.
        """
        unwrapped = container.unwrap(args)
        indices = _index.resolve(self.shape, unwrapped)
        loaded = self._load_array(indices)
        array = numpy.array(loaded, ndmin=self.ndim)
        if isinstance(indices, numpy.ndarray) and indices.dtype == bool:
            return array
        if loaded.ndim != self.ndim:
            with contextlib.suppress(TypeError):
                shape = [
                    self._get_axis_size(i, v)
                    for i, v in enumerate(indices)
                ]
                return array.reshape(shape)
        return array

    def _get_axis_size(self, i: int, v):
        """Helper for computing shape in `__getitem__`."""
        if isinstance(v, int):
            return 1
        if isinstance(v, slice):
            return (v.stop or self.shape[i]) - (v.start or 0)
        return self.shape[i]

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return self._as_string()

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        return self._as_string(
            prefix=f'{self.__class__.__qualname__}(',
            suffix=')',
        )

    def _as_string(self, prefix: str='', suffix: str='') -> str:
        """Create a string representation of this object."""
        data = self._format_data(prefix=prefix, suffix=suffix)
        dimensions = f"dimensions={self.dimensions}"
        return f"{prefix}{data}, {dimensions}{suffix}"

    def _format_data(self, **kwargs):
        """Create an appropriate string to represent the data."""
        if not isinstance(self._object, numpy.ndarray):
            return str(type(self._object))
        try:
            signed = '+' if any(i < 0 for i in self.array.flat) else '-'
        except TypeError:
            # If we get here, it's probably because some values are strings
            signed = '-'
        return numpy.array2string(
            self.array,
            threshold=4,
            edgeitems=2,
            separator=', ',
            sign=signed,
            precision=3,
            floatmode='maxprec_equal',
            **kwargs
        )

    def __array__(self, *args, **kwargs) -> numpy.ndarray:
        """Support casting to `numpy` array types.
        
        Notes
        -----
        This will retrieve the underlying array before applying `*args` and
        `**kwargs`, in order to avoid a `TypeError` when using
        `netCDF4.Dataset`. See
        https://github.com/mcgibbon/python-examples/blob/master/scripts/file-io/load_netCDF4_full.py
        """
        array = self.array
        return numpy.asarray(array, *args, **kwargs)

    def remesh(self, other, invert: bool=False):
        """Construct array meshes for broadcasting.

        This method calls `~remesh` to reshape the arrays of both data
        interfaces in a way that is consistent with their combined dimensions.

        Parameters
        ----------
        other : `~Data`
            The data interface with which to mutually reshape.
        invert : bool, default=false
            If true, reverse the order of `self` and `other`.
        """
        if invert:
            return remesh(other, self)
        return remesh(self, other)

    def contains(self, value: numbers.Real) -> bool:
        """True if `value` is in this sequence's data array.

        This method uses `~numeric.data.isclose` to test whether `value` is
        equal, or very close, to a value in this object's real-valued data.

        Parameters
        ----------
        value : real
            The value for which to search.
        
        See Also
        --------
        `~numeric.data.isclose`
        """
        return _data.isclose(self, value)

    @typing.overload
    def transpose(
        self,
        axes: typing.Iterable[typing.Union[str, typing.SupportsIndex]],
        /,
    ) -> Self: ...

    @typing.overload
    def transpose(
        self,
        *axes: typing.Union[str, typing.SupportsIndex],
    ) -> Self: ...

    def transpose(self, *args):
        """Transpose this array."""
        if not args:
            return self
        if etc.allisinstance(str, *args):
            return self._transpose(args)
        if len(args) == 1:
            arg = args[0]
            if etc.allisinstance(str, *arg):
                return self._transpose(arg)
        data = self.array.transpose(*args)
        new = self.dimensions.permute(*args)
        return self.spawn(data, dimensions=new)

    def _transpose(self, args: typing.Iterable[str]):
        """Helper for `~transpose`."""
        self.dimensions.mismatch(args)
        axes = [self.dimensions.index(arg) for arg in args]
        data = self.array.transpose(axes)
        return self.spawn(data, dimensions=args)

    @property
    def size(self) -> int:
        """The number of elements in this array."""
        return self._size

    @property
    def array(self):
        """The underlying array-like data interface."""
        if self._array is None:
            self._array = self._load_array()
        return self._array

    def _load_array(
        self,
        index: typing.Optional[IndexLike]=None,
    ) -> numpy.typing.NDArray:
        """Load the array from disk or memory.

        This method is intended for internal use. Users should subscript
        instances via bracket notation (e.g., `array[:, 2]`).

        If `index` is `None` or an empty iterable, this method will produce the
        entire array. Otherwise, it will create the requested subarray from the
        internal `_data` attribute. It will always attempt to use a cached
        version of the full array before loading from disk. Therefore,
        repeatedly calling this method should not create a performance
        bottleneck.

        The specific algorithm is as follows:

        - If `index` is null (i.e., `None` or an empty iterable object, but not
          literal 0), the caller wants the full array.
        
            - If we already have the full array, return it.
            - Else, read it, save it, and return it.

        - Else, if `index` is not null, the caller wants a subarray.

            - If we already have the full array, subscript and return it.
            - Else, continue

        - Else, read and subscript the array, and return the subarray.

        The reasoning behind this algorithm is as follows: If we need to load
        the full array at any point, we may as well save it because subscripting
        an in-memory `numpy.ndarray` is much faster than re-reading from disk
        for large arrays. However, we should avoid reading in the full array if
        the caller only wants a small portion of it. We don't cache these
        subarrays because reusing a subarray is only meaningful if the indices
        haven't changed. Furthermore, accessing a subarray via bracket syntax
        creates a new object, at which point the subarray becomes the new
        object's full array.
        """
        if etc.isnull(index):
            if self._array is not None:
                return self._array
            array = self._read_array()
            self._array = array
            return array
        if self._array is not None:
            idx = numpy.index_exp[index]
            return self._array[idx]
        return self._read_array(index)

    def _read_array(
        self,
        index: typing.Optional[IndexLike]=None,
    ) -> numpy.typing.NDArray:
        """Read the array data from disk.
        
        If `index` is null in the sense defined by `~etc.isnull` this method
        will load and return the full array. If `index` is not null, this method
        will first attempt to subscript the internal `_data` attribute before
        converting it to an array and returning it. If it catches either a
        `TypeError` or an `IndexError`, it will create the full array before
        subscripting and returning it. The former may occur if the internal
        `_data` attribute is a sequence type like `list`, `tuple`, or `range`;
        the latter may occur when attempting to subscript certain array-like
        objects (e.g., `netCDF4._netCDF4.Variable`) despite passing a valid
        `numpy` index expression.
        """
        if not etc.isnull(index):
            idx = numpy.index_exp[index]
            try:
                return numpy.asarray(self._object[idx])
            except (TypeError, IndexError):
                return numpy.asarray(self._object)[idx]
        return numpy.asarray(self._object)

    @property
    def shapemap(self) -> typing.Dict[str, int]:
        """The name and size of each axis."""
        return dict(zip(self.dimensions, self.shape))

    @property
    def dimensions(self) -> Dimensions:
        """The names of this array's indexable axes."""
        return self._dimensions

    @property
    def ndim(self) -> int:
        """The number of dimensions in this array."""
        return self._ndim

    @property
    def shape(self) -> typing.Tuple[int]:
        """The length of each dimension in this array."""
        return self._shape

    def _get_arg_data(self, arg):
        if isinstance(arg, Array):
            return self.array
        return super()._get_arg_data(arg)

    _FUNCTIONS = {}
    _OPERATORS = {}


Array._UFUNC_TYPES += [Array]
Array._FUNCTION_TYPES += [Array]


ArrayType = typing.TypeVar('ArrayType', bound=Array)


@Array.implements(numpy.array_equal)
def array_equal(a: Array, b: Array) -> bool:
    """Called for numpy.array_equal(a, b)."""
    return numpy.array_equal(numpy.array(a), numpy.array(b))


@typing.overload
def array_factory(*args, **kwargs) -> Array:
    """Create an array-like quantity from the given arguments, if possible."""

@typing.overload
def array_factory(x, /) -> Array:
    """Create an array-like quantity from `x`.

    This function will construct default dimension names based on the number of
    dimensions in `x`.
    """

@typing.overload
def array_factory(x, /, dimensions: typing.Iterable[str]) -> Array:
    """Create an array-like quantity from `x`.

    This function will use the strings in `dimensions` as the dimension names.
    The length of `dimensions` must equal the number of dimensions in `x`.
    """

@typing.overload
def array_factory(x, *dimensions: str) -> Array:
    """Create an array-like quantity from `x`.

    This function will use the string arguments following `x` as the dimension
    names. The number of strings must equal the number of dimensions in `x`.
    """

@typing.overload
def array_factory(x: ArrayType, /) -> ArrayType:
    """Create an array-like quantity from `x`.

    This function will copy array data and dimensions from `x`.
    """

def array_factory(*args, **kwargs):
    return Array(*array_args(*args, **kwargs))

def array_args(*args, **kwargs):
    if len(args) == 1:
        x = args[0]
        if isinstance(x, Array):
            if kwargs:
                raise TypeError(
                    "Cannot change attributes when copying"
                    " an existing quantity"
                ) from None
            return x.array, x.dimensions
    array, dimensions = _parse_data_args(*args, **kwargs)
    if len(dimensions) != array.ndim:
        raise ValueError(
            f"Number of named dimensions ({len(dimensions)})"
            f" must equal number of array dimensions ({array.ndim})"
        ) from None
    return array, dimensions


def _parse_data_args(*args, dimensions=None):
    """Parse arguments for initializing a data interface."""
    array = _init_array(args[0])
    if len(args) > 1:
        if dimensions:
            raise TypeError(
                "Got positional and keyword arguments for dimensions"
            ) from None
        return array, dimensions_factory(args[1:])
    if dimensions is None:
        return array, dimensions_factory(array.ndim)
    return array, dimensions_factory(dimensions)


def _init_array(arg) -> base.Array:
    """Get an array-like data interface.
    
    This method ensures that calling methods get an object that has certain
    array-like properties, without requiring that `arg` be an instance of
    `numpy.ndarray` and without converting `arg` to a `numpy.ndarray` unless
    necessary.
    """
    data = _get_arraylike(arg)
    # NOTE: This attribute check is more robust than testing whether `data`
    # satisfies the `quantity.Array` protocol, which requires that the target
    # object define these attribute as properties.
    if all(hasattr(data, name) for name in ('shape', 'ndim', 'size')):
        return data
    return numpy.array(data)


def _get_arraylike(arg):
    """Extract an array-like interface from `arg`."""
    if isinstance(arg, Object):
        return arg.data
    if isinstance(arg, (list, tuple, set)):
        return numpy.array(arg)
    return arg


def remesh(a: Array, b: Array):
    """Construct array meshes for broadcasting.
    
    This function mutually reshapes the internal `numpy` arrays of two data
    interfaces based on their combined dimensions. The result is a pair of
    `numpy` arrays that can broadcast together while preserving a shape
    consistent with the combined dimensions.

    Parameters
    ----------
    a, b : `~numeric.Array`
        The numeric arrays to reshape.

    Returns
    -------
    `tuple` of `numpy.ndarray`
        The reshaped `numpy` array of `a`, followed by that of `b`.

    Raises
    ------
    `TypeError`
        One or both of the arguments was not an instance of `~numeric.Array`.
    `ValueError`
        The original array shapes of `a` and `b` have incompatible shapes and
        dimensions. Note that this case acts like the `ValueError` raised when
        attempting to broadcast two `numpy` arrays with inconsistent shapes.
    """
    if not (isinstance(a, Array) and isinstance(b, Array)):
        raise TypeError(
            f"Both arguments must be instances of {Array!r}"
        ) from None
    dimensions = a.dimensions | b.dimensions
    for d in dimensions:
        adim = a.shapemap.get(d, 1)
        bdim = b.shapemap.get(d, 1)
        if adim > 1 and bdim > 1 and adim != bdim:
            # NOTE: This acts like the `ValueError` raised when attempting
            # to broadcast two `numpy` arrays with inconsistent shapes.
            raise ValueError(
                "Cannot create a mesh from arrays with"
                f" dimensions {a.dimensions} and {b.dimensions}"
                ", and corresponding shapes"
                f" shapes {a.shape} and {b.shape}"
            )
    ndim = len(dimensions)
    shape = tuple(
        # NOTE: This creates the maximal shape in order to handle cases in
        # which the input arrays have matching dimensions but one array is
        # singular. The previous implementation would always overwrite the
        # size of matching dimensions in `a` with those of `b`.
        max(a.shapemap.get(d, 1), b.shapemap.get(d, 1))
        for d in dimensions
    )
    idxmesh = numpy.ix_(*[range(i) for i in shape])
    idxa = tuple(idxmesh[dimensions.index(d)] for d in a.shapemap)
    idxb = tuple(idxmesh[dimensions.index(d)] for d in b.shapemap)
    x = numpy.array(a, ndmin=ndim) if a.size == 1 else a._load_array(idxa)
    y = numpy.array(b, ndmin=ndim) if b.size == 1 else b._load_array(idxb)
    return x, y


