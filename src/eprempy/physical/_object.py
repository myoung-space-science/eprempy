import abc
import typing

from .. import base
from .. import measured
from .. import numeric
from .. import quantity
from ..typehelp import Self
from ._types import QuantityType as Q


class Operators(numeric.Operators, abc.ABC):
    """Abstract mixin class for custom physical operations."""

    @abc.abstractmethod
    def __eq__(self, other):
        """Called for self == other."""

    @abc.abstractmethod
    def __ne__(self, other):
        """Called for self != other."""

    @abc.abstractmethod
    def __lt__(self: Self, other) -> typing.Any:
        """Called for self < other."""

    @abc.abstractmethod
    def __gt__(self: Self, other) -> typing.Any:
        """Called for self > other."""

    @abc.abstractmethod
    def __le__(self: Self, other) -> typing.Any:
        """Called for self <= other."""

    @abc.abstractmethod
    def __ge__(self: Self, other) -> typing.Any:
        """Called for self >= other."""

    @abc.abstractmethod
    def __abs__(self: Self) -> Self:
        """Called for abs(self: Self)."""

    @abc.abstractmethod
    def __pos__(self: Self) -> Self:
        """Called for +self."""

    @abc.abstractmethod
    def __neg__(self: Self) -> Self:
        """Called for -self."""

    @abc.abstractmethod
    def __add__(self: Self, other) -> Self:
        """Called for self + other."""

    @abc.abstractmethod
    def __radd__(self: Self, other) -> Self:
        """Called for other + self."""

    @abc.abstractmethod
    def __sub__(self: Self, other) -> Self:
        """Called for self - other."""

    @abc.abstractmethod
    def __rsub__(self: Self, other) -> Self:
        """Called for other - self."""

    @abc.abstractmethod
    def __mul__(self: Self, other) -> Self:
        """Called for self * other."""

    @abc.abstractmethod
    def __rmul__(self: Self, other) -> Self:
        """Called for other * self."""

    @abc.abstractmethod
    def __truediv__(self: Self, other) -> Self:
        """Called for self / other."""

    @abc.abstractmethod
    def __rtruediv__(self: Self, other) -> Self:
        """Called for other / self."""

    @abc.abstractmethod
    def __floordiv__(self: Self, other) -> Self:
        """Called for self // other."""

    @abc.abstractmethod
    def __rfloordiv__(self: Self, other) -> Self:
        """Called for other // self."""

    @abc.abstractmethod
    def __mod__(self: Self, other) -> Self:
        """Called for self % other."""

    @abc.abstractmethod
    def __rmod__(self: Self, other) -> Self:
        """Called for other % self."""

    @abc.abstractmethod
    def __pow__(self: Self, other) -> Self:
        """Called for self ** other."""

    @abc.abstractmethod
    def __rpow__(self: Self, other) -> Self:
        """Called for other ** self."""


class Object(measured.Object[base.RealType], Operators):
    """A real-valued measurable object."""

    def __init__(
        self,
        data: base.RealType,
        context: measured.Context[Q],
        /,
    ) -> None:
        super().__init__(data, context)

    def __measure__(self) -> quantity.Measurement:
        return quantity.measurement(self.data, unit=self.unit)

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


ObjectT = typing.TypeVar('ObjectT', bound=Object)
"""Type variable bound to `~physical.Object`."""


