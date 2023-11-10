import abc
import typing

import numpy

from .. import base
from .. import container
from .. import numeric
from ._types import ValueType


T = typing.TypeVar('T')


class Variable(numeric.Object[ValueType], base.abc.Sequence):
    """A sequence-like object with conditional cast to built-in type.
    
    An instance of this class behaves like a sequence of real values, and
    additionally supports converting single-valued instances to built-in `int`,
    `float`, or `complex` type.

    See Also
    --------
    `~quantity.abc.Sequence`
    """

    def __init__(self, data: typing.Sequence[ValueType]) -> None:
        super().__init__(data)
        self._size = None

    def __int__(self) -> int:
        """Called for int(self)."""
        return self._cast_to(int)

    def __float__(self) -> float:
        """Called for float(self)."""
        return self._cast_to(float)

    def __complex__(self) -> complex:
        """Called for complex(self)."""
        return self._cast_to(complex)

    def _cast_to(self, __type: typing.Type[T]) -> T:
        """Internal logic for casting data to type `T`."""
        if self.size == 1:
            return __type(self.data[0])
        raise TypeError(
            f"Cannot convert size-{self.size} object to float"
        ) from None

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, i: typing.SupportsIndex):
        return self.data[i]

    def __array__(self, *args, **kwargs) -> numpy.ndarray:
        """Called to convert this variable to a `numpy.ndarray`.
        
        Notes
        -----
        - This method converts an instance to a `numpy.ndarray` by calling
          `numpy.asarray` on the underlying data. Therefore, if the data is
          already a `numpy.ndarray`, calling `numpy.asarray` on this instance
          will return the original array.
        """
        return numpy.asarray(self.data, *args, **kwargs)

    @property
    def size(self) -> int:
        """The number of numerical values in this instance."""
        if self._size is None:
            self._size = container.size(self._data)
        return self._size


class Quantity(base.abc.Real):
    """Partial implementation of the real-valued protocol."""

    # NOTE: The body of this class defines all real-valued methods in order to
    # add type annotations. Many of these definitions simply call back to the
    # parent ABC and therefore remain abstract.

    # (abstract)
    def __eq__(self: base.RealType, other) -> bool:
        return super().__eq__(other)

    # (concrete)
    def __ne__(self: base.RealType, other) -> bool:
        return not (self == other)

    # (abstract)
    def __lt__(self: base.RealType, other) -> bool:
        return super().__lt__(other)

    # (concrete)
    def __le__(self: base.RealType, other) -> bool:
        return self < other or self == other

    # (concrete)
    def __gt__(self: base.RealType, other) -> bool:
        return not (self < other or self == other)

    # (concrete)
    def __ge__(self: base.RealType, other) -> bool:
        return not (self < other)

    # (abstract)
    def __abs__(self: base.RealType) -> base.RealType:
        return super().__abs__()

    # (abstract)
    def __pos__(self: base.RealType) -> base.RealType:
        return super().__pos__()

    # (abstract)
    def __neg__(self: base.RealType) -> base.RealType:
        return super().__neg__()

    # (abstract)
    def __add__(self: base.RealType, other) -> base.RealType:
        return super().__add__(other)

    # (abstract)
    def __radd__(self: base.RealType, other) -> base.RealType:
        return super().__radd__(other)

    # (concrete)
    def __sub__(self: base.RealType, other) -> base.RealType:
        return self + (-other)

    # (concrete)
    def __rsub__(self: base.RealType, other) -> base.RealType:
        return other + (-self)

    # (abstract)
    def __mul__(self: base.RealType, other) -> base.RealType:
        return super().__mul__(other)

    # (abstract)
    def __rmul__(self: base.RealType, other) -> base.RealType:
        return super().__rmul__(other)

    # (abstract)
    def __truediv__(self: base.RealType, other) -> base.RealType:
        return super().__truediv__(other)

    # (abstract)
    def __rtruediv__(self: base.RealType, other) -> base.RealType:
        return super().__rtruediv__(other)

    # (abstract)
    def __pow__(self: base.RealType, other) -> base.RealType:
        return super().__pow__(other)

    @abc.abstractmethod
    def __floordiv__(self, other):
        """Called for self // other."""

    @abc.abstractmethod
    def __rfloordiv__(self, other):
        """Called for other // self."""

    @abc.abstractmethod
    def __mod__(self, other):
        """Called for self % other."""

    @abc.abstractmethod
    def __rmod__(self, other):
        """Called for other % self."""


