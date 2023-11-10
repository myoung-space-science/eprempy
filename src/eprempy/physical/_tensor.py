import numpy

from .. import base
from .. import measured
from ._object import Object
from ._scalar import Scalar
from ._types import QuantityType as Q


class Tensor(Object[base.ArrayType]):
    """A multi-dimensional physical object."""

    def __init__(
        self,
        data: base.ArrayType,
        context: measured.Context[Q],
        /,
    ) -> None:
        if not isinstance(data, base.Array):
            raise TypeError(
                f"Data argument to {type(self)} must implement"
                f" the {base.Array} protocol"
            )
        super().__init__(data, context)
        self._size = data.size
        self._ndim = data.ndim
        self._shape = data.shape

    def __contains__(self, v) -> bool:
        """Called for v in self."""
        return v in self.data

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.data)

    def __iter__(self):
        """Called for iter(self)."""
        flatdata = numpy.array(self.data).flat
        return (Scalar.spawn(x, unit=self.unit) for x in flatdata)

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
        """The number of data values in this tensor."""
        return self._size

    @property
    def ndim(self) -> int:
        """The number of dimensions in this tensor's data."""
        return self._ndim

    @property
    def shape(self) -> int:
        """The length of each dimension in this tensor's data."""
        return self._shape

    def _get_numpy_array(self):
        return numpy.array(self.data)

    _FUNCTIONS = {}
    _OPERATORS = {}


