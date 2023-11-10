import typing

import numpy

from .. import base
from .. import container
from .. import real
from ._context import Context
from ._object import (
    Object,
    ObjectT,
)
from ._value import Value


class Sequence(Object[real.ValueType], base.mixins.Sequence):
    """A measured object with multiple values.

    See Also
    --------
    `~Object`
        An object with real-valued data and an associated unit.
    `~base.Sequence`
        The abstract protocol for sequence-like objects.
    `~base.mixins.Sequence`
        A partial implementation of the sequence-like protocol.
    """

    def __init__(
        self,
        data: typing.Sequence[real.ValueType],
        context: Context[ObjectT],
        /,
    ) -> None:
        super().__init__(data, context)
        self._size = None

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> typing.Iterator[Value]:
        return super().__iter__()

    def __getitem__(self, i: typing.SupportsIndex):
        data = self.data[i]
        # NOTE: A measured sequence should return a single measured value when
        # the subscripted data represents a single value. This is consistent
        # with the behavior of built-in sequences and numpy arrays. We approach
        # this problem by naively trying to create a measured value from the
        # subscripted data and returning that value if we succeeded. If anything
        # goes wrong when trying to create the measured value, we assume that
        # the subscripted data does not represent a single value, and return a
        # new measured sequence.
        try:
            result = Value.spawn(data, unit=self.unit)
        except TypeError:
            result = self.spawn(data, unit=self.unit)
        return result

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
            self._size = container.size(self.data)
        return self._size


