import typing

import numpy

from .. import base
from .. import measured
from ..typehelp import Self
from ._object import Object
from ._scalar import Scalar
from ._types import QuantityType as Q


class Vector(Object[base.SequenceType]):
    """A one-dimensional physical object."""

    def __init__(
        self,
        data: base.SequenceType,
        context: measured.Context[Q],
        /,
    ) -> None:
        array = numpy.asanyarray(data)
        super().__init__(array, context)
        self._size = array.size

    def __contains__(self, v) -> bool:
        """Called for v in self."""
        return v in self.data

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.data)

    def __iter__(self):
        """Called for iter(self)."""
        return (Scalar.spawn(x, unit=self.unit) for x in self.data)

    @typing.overload
    def __getitem__(self, __i: int) -> Scalar: ...

    @typing.overload
    def __getitem__(self: Self, __i: slice) -> Self: ...

    def __getitem__(self, __i):
        """Called for self[__i]."""
        data = self.data[__i]
        try:
            result = Scalar.spawn(data, unit=self.unit)
        except TypeError:
            result = self.spawn(data, unit=self.unit)
        return result

    def __array__(self, *args, **kwargs) -> numpy.ndarray:
        """Called for conversion to a native `numpy` array."""
        return numpy.array(self.data, *args, **kwargs)

    @property
    def size(self) -> int:
        """The number of data values in this vector."""
        return self._size

    def _get_numpy_array(self):
        return numpy.array(self.data)

    _FUNCTIONS = {}
    _OPERATORS = {}


