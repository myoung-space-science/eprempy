"""
Abstract base classes corresponding to runtime protocols.
"""

import abc
import typing

import numpy

from .. import etc


A = typing.TypeVar('A')
B = typing.TypeVar('B')
R = typing.TypeVar('R')

BoolT = typing.Union[bool, typing.Sequence[bool]]


class Quantity(abc.ABC):
    """Abstract base class for all quantities.
    
    Similar in spirit to `numbers.Number`.
    """

    __slots__ = ()

    __hash__ = None


class Ordered(Quantity):
    """Abstract base class for ordered objects.

    A concrete implementation must define the following methods

    - `__lt__` (less than: `a < b`)
    - `__le__` (less than or equal: `a <= b`)
    - `__gt__` (greater than: `a > b`)
    - `__ge__` (greater than or equal: `a >= b`)

    See Also
    --------
    `~quantity.Ordered`
        The corresponding abstract protocol.
    """

    __slots__ = ()

    @abc.abstractmethod
    def __lt__(self, other) -> BoolT:
        """Called for self < other."""

    @abc.abstractmethod
    def __le__(self, other) -> BoolT:
        """Called for self <= other."""

    @abc.abstractmethod
    def __gt__(self, other) -> BoolT:
        """Called for self > other."""

    @abc.abstractmethod
    def __ge__(self, other) -> BoolT:
        """Called for self >= other."""


class Comparable(Ordered):
    """Abstract base class for comparable objects.

    A concrete implementation must define the following methods

    - `__eq__` (equal: `a == b`)
    - `__ne__` (not equal: `a != b`)
    - `__lt__` (inherited from `~Ordered`)
    - `__le__` (inherited from `~Ordered`)
    - `__gt__` (inherited from `~Ordered`)
    - `__ge__` (inherited from `~Ordered`)

    See Also
    --------
    `~quantity.Comparable`
        The corresponding abstract protocol.
    `~Ordered`
        Abstract base class for ordered objects.
    """

    __slots__ = ()

    @abc.abstractmethod
    def __eq__(self, other) -> BoolT:
        """Called for self == other."""

    @abc.abstractmethod
    def __ne__(self, other) -> BoolT:
        """Called for self != other."""


class Additive(Quantity):
    """Abstract base class for additive objects.

    A concrete implementation must define the following methods

    - `__add__`  (addition: `a + b`)
    - `__radd__` (addition with reflected operands: `b + a`)
    - `__sub__`  (subtraction: `a - b`)
    - `__rsub__` (subtraction with reflected operands: `b - a`)

    See Also
    --------
    `~quantity.Additive`
        The corresponding abstract protocol.
    """

    __slots__ = ()

    @abc.abstractmethod
    def __add__(self: A, other: B) -> typing.Union[A, B]:
        """Called for self + other."""

    @abc.abstractmethod
    def __radd__(self: A, other: B) -> typing.Union[A, B]:
        """Called for other + self."""

    @abc.abstractmethod
    def __sub__(self: A, other: B) -> typing.Union[A, B]:
        """Called for self - other."""

    @abc.abstractmethod
    def __rsub__(self: A, other: B) -> typing.Union[A, B]:
        """Called for other - self."""


class Multiplicative(Quantity):
    """Abstract base class for multiplicative objects.

    A concrete implementation must define the following methods

    - `__mul__`      (multiplication: `a * b`)
    - `__rmul__`     (multiplication with reflected operands: `b * a`)
    - `__truediv__`  (division: `a / b`)
    - `__rtruediv__` (division with reflected operands: `b / a`)

    See Also
    --------
    `~quantity.Multiplicative`
        The corresponding abstract protocol.
    """

    __slots__ = ()

    @abc.abstractmethod
    def __mul__(self: A, other: B) -> typing.Union[A, B]:
        """Called for self * other."""

    @abc.abstractmethod
    def __rmul__(self: A, other: B) -> typing.Union[A, B]:
        """Called for other * self."""

    @abc.abstractmethod
    def __truediv__(self: A, other: B) -> typing.Union[A, B]:
        """Called for self / other."""

    @abc.abstractmethod
    def __rtruediv__(self: A, other: B) -> typing.Union[A, B]:
        """Called for other / self."""


class Algebraic(Additive, Multiplicative):
    """Abstract base class for algebraic objects.
    
    A concrete implementation must define the following methods

    - `__add__`      (inherited from `~Additive`)
    - `__radd__`     (inherited from `~Additive`)
    - `__sub__`      (inherited from `~Additive`)
    - `__rsub__`     (inherited from `~Additive`)
    - `__mul__`      (inherited from `~Multiplicative`)
    - `__rmul__`     (inherited from `~Multiplicative`)
    - `__truediv__`  (inherited from `~Multiplicative`)
    - `__rtruediv__` (inherited from `~Multiplicative`)
    - `__pow__`      (exponentiation: `a ** b`)

    See Also
    --------
    `~quantity.Algebraic`
        The corresponding abstract protocol.
    `~Additive`
        Abstract base class for additive objects.
    `~Multiplicative`
        Abstract base class for multiplicative objects.
    """

    __slots__ = ()

    @abc.abstractmethod
    def __pow__(self: A, other: B) -> typing.Union[A, B]:
        """Called for self ** other."""


class Complex(Algebraic):
    """Abstract base class for complex-valued objects.

    A concrete implementation must define all methods required by `~Algebraic`,
    as well as the following methods

    - `__abs__` (absolute value: `abs(a)`)
    - `__pos__` (positive: `+a`)
    - `__neg__` (negative: `-a`)

    See Also
    --------
    `~quantity.Complex`
        The corresponding abstract protocol
    `~Algebraic`
        Abstract base class for algebraic objects.
    """

    __slots__ = ()

    @abc.abstractmethod
    def __abs__(self: A) -> A:
        """Called for abs(self)."""

    @abc.abstractmethod
    def __pos__(self: A) -> A:
        """Called for +self."""

    @abc.abstractmethod
    def __neg__(self: A) -> A:
        """Called for -self."""


class Real(Comparable, Complex):
    """Abstract base class for real-valued objects.

    This ABC is designed to encapsulate the behavior of objects that provide an
    interface to, or a container for, real-valued numerical data. It exists
    outside of the `numbers.Number` hierarchy in order to equally support
    single-valued and multi-valued objects.

    A concrete real-valued object must implement all methods required by the
    `~quantity.Real` protocol. Those include the following binary comparison
    operators

    - `__eq__` (inherited from `~Comparable`)
    - `__ne__` (inherited from `~Comparable`)
    - `__lt__` (inherited from `~Comparable`)
    - `__le__` (inherited from `~Comparable`)
    - `__gt__` (inherited from `~Comparable`)
    - `__ge__` (inherited from `~Comparable`)

    the following unary arithmetic operators

    - `__abs__` (inherited from `~Complex`)
    - `__pos__` (inherited from `~Complex`)
    - `__neg__` (inherited from `~Complex`)

    and the following binary arithmetic operators

    - `__add__`       (inherited from `~Algebraic`)
    - `__radd__`      (inherited from `~Algebraic`)
    - `__sub__`       (inherited from `~Algebraic`)
    - `__rsub__`      (inherited from `~Algebraic`)
    - `__mul__`       (inherited from `~Algebraic`)
    - `__rmul__`      (inherited from `~Algebraic`)
    - `__truediv__`   (inherited from `~Algebraic`)
    - `__rtruediv__`  (inherited from `~Algebraic`)
    - `__pow__`       (inherited from `~Algebraic`)
    - `__rpow__`      (exponentiation with reflected operands: `b ** a`)
    - `__floordiv__`  (floor division: `a // b`)
    - `__rfloordiv__` (floor division with reflected operands: `b // a`)
    - `__mod__`       (modular division: `a % b`)
    - `__rmod__`      (modular division with reflected operands: `b % a`)

    See https://docs.python.org/3/reference/datamodel.html for a description of
    each method and implementation suggestions.

    See Also
    --------
    `~quantity.Real`
        The corresponding abstract protocol.
    `~Comparable`
        Abstract base class for comparable objects.
    `~Complex`
        Abstract base class for complex-valued objects.
    """

    __slots__ = ()

    @abc.abstractmethod
    def __rpow__(self: A, other: B) -> typing.Union[A, B]:
        """Called for other ** self."""

    @abc.abstractmethod
    def __floordiv__(self: A, other: B) -> typing.Union[A, B]:
        """Called for self // other."""

    @abc.abstractmethod
    def __rfloordiv__(self: A, other: B) -> typing.Union[A, B]:
        """Called for other // self."""

    @abc.abstractmethod
    def __mod__(self: A, other: B) -> typing.Union[A, B]:
        """Called for self % other."""

    @abc.abstractmethod
    def __rmod__(self: A, other: B) -> typing.Union[A, B]:
        """Called for other % self."""


@etc.autostr
class Scalar(Real):
    """ABC for singular real-valued objects.
    
    A concrete scalar object must implement all methods required by the
    `~quantity.Scalar` protocol. In addition to those required by the
    `~quantity.Real` protocol, they include the following

    - `__int__`
    - `__floor__`
    - `__complex__`
    - `__round__`

    See Also
    --------
    `~quantity.Scalar`
        The corresponding abstract protocol.
    `~Real`
        Abstract base class for real-valued objects.
    """

    __slots__ = ()

    @abc.abstractmethod
    def __int__(self) -> int:
        """Called for int(self)."""

    @abc.abstractmethod
    def __float__(self) -> float:
        """Called for float(self)."""

    @abc.abstractmethod
    def __complex__(self) -> complex:
        """Called for complex(self)."""

    @abc.abstractmethod
    def __round__(self: A) -> A:
        """Called for round(self)."""


@etc.autostr
class Sequence(Quantity):
    """Abstract base class for sequence-like objects.

    A concrete implementation must default the following methods

    - `__contains__`
    - `__len__`
    - `__iter__`
    - `__getitem__`
    - `__array__`

    See Also
    --------
    `~quantity.Sequence`
        The corresponding abstract protocol.
    """

    __slots__ = ()

    @abc.abstractmethod
    def __contains__(self, v, /) -> bool:
        """Called for v in self."""

    @abc.abstractmethod
    def __len__(self) -> int:
        """Called for len(self)."""

    @abc.abstractmethod
    def __iter__(self) -> typing.Iterator:
        """Called for iter(self)."""

    @abc.abstractmethod
    def __getitem__(self, i: typing.SupportsIndex, /):
        """Called for self[i]."""

    @abc.abstractmethod
    def __array__(self, *args, **kwargs) -> numpy.ndarray:
        """Called for conversion to a `numpy.ndarray`."""


@etc.autostr
class Array(Sequence):
    """ABC for array-like objects.
    
    A concrete implementation must define all the methods and properties
    required by the `~quantity.Array` protocol. Those include the following
    methods (inherited from `~Sequence`)

    - `__iter__`
    - `__contains__`
    - `__len__`
    - `__getitem__`
    - `__array__`

    and the following properties

    - `size`
    - `ndim`
    - `shape`

    See Also
    --------
    `~quantity.Array`
        The corresponding abstract protocol.
    `~Sequence`
        Abstract base class for sequence-like objects.
    """

    __slots__ = ()

    @property
    @abc.abstractmethod
    def size(self) -> int:
        """The total number of values in this array."""

    @property
    @abc.abstractmethod
    def ndim(self) -> int:
        """The number of dimensions in this array."""

    @property
    @abc.abstractmethod
    def shape(self) -> typing.Tuple[int]:
        """The length of each dimension in this array."""

