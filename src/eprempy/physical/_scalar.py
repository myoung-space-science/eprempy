import abc
import numpy

from .. import base
from .. import exceptions
from .. import measured
from .. import numeric
from .. import real
from ._exceptions import PhysicalTypeError
from ._object import (
    Object,
)
from ._types import QuantityType as Q


class Operators(abc.ABC):
    """Abstract base class for physical scalar operators."""

    @abc.abstractmethod
    def __round__(self: Q, ndigits: int=None) -> Q:
        """Called for round(self)."""

    @abc.abstractmethod
    def __floor__(self: Q) -> Q:
        """Called for math.floor(self)."""

    @abc.abstractmethod
    def __ceil__(self: Q) -> Q:
        """Called for math.ceil(self)."""

    @abc.abstractmethod
    def __trunc__(self: Q) -> Q:
        """Called for math.trunc(self)."""


class Scalar(Object[real.ValueType], Operators):
    """A single-valued physical object."""

    def __init__(
        self,
        data: real.ValueType,
        context: measured.Context[Q],
        /,
    ) -> None:
        if not isinstance(data, base.Scalar):
            raise TypeError(
                f"Data argument to {type(self)} must implement"
                f" the {base.Scalar} protocol"
            ) from None
        super().__init__(data, context)

    @exceptions.convert(PhysicalTypeError, TypeError)
    def __int__(self) -> int:
        """Called for int(self)."""
        if operator := self._OPERATORS.get(int):
            return operator(self)
        raise TypeError(
            f"Instances of {type(self)} do not support"
            f" conversion to built-in {int} type"
        ) from None

    @exceptions.convert(PhysicalTypeError, TypeError)
    def __float__(self) -> float:
        """Called for float(self)."""
        if operator := self._OPERATORS.get(float):
            return operator(self)
        raise TypeError(
            f"Instances of {type(self)} do not support"
            f" conversion to built-in {float} type"
        ) from None

    @exceptions.convert(PhysicalTypeError, TypeError)
    def __complex__(self) -> complex:
        """Called for complex(self)."""
        if operator := self._OPERATORS.get('complex'):
            return operator(self)
        raise TypeError(
            f"Instances of {type(self)} do not support"
            f" conversion to built-in {complex} type"
        ) from None

    __round__ = numeric.implementation.unary('round')
    __floor__ = numeric.implementation.unary('floor')
    __ceil__ = numeric.implementation.unary('ceil')
    __trunc__ = numeric.implementation.unary('trunc')

    def _get_numpy_array(self):
        return numpy.array(self.data)

    _FUNCTIONS = {}
    _OPERATORS = {}


