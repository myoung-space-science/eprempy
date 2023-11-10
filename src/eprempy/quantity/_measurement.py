import typing

import numpy

from .. import base
from .. import container
from .. import measured
from .. import numeric
from .. import real


T = typing.TypeVar('T')


class Measurement(measured.Sequence[real.ValueType]):
    """A physical measurement.
    
    An instance of this class behaves like a numeric sequence, and additionally
    supports converting single-valued instances to built-in `int`, `float`, or
    `complex` type. It also inherits unit support from `~measured.Object`.

    See Also
    --------
    `~measured.Sequence`
        A sequence of real values with an associated metric unit.
    """

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
            f"Cannot convert size-{self.size} sequence to float"
        ) from None


@Measurement.register.factory
def measurement_factory(x, /, unit=None):
    """Factory function for `~Measurement`."""
    d, u = measurement_args(x, unit)
    ctx = measured.context(u, measured.convert.arraylike)
    return Measurement(d, ctx)


def measurement_args(x, unit, /):
    if isinstance(x, measured.Object):
        sequence = measured.sequence(x)
        return sequence.data, sequence.unit
    if container.isseparable(x):
        if numeric.data.hasdtype(x, (numpy.integer, numpy.floating)):
            return numpy.array(x), unit
        raise TypeError(
            f"Cannot create a measurement from {x!r}"
            " with non-numeric values."
        )
    if not base.isreal(x):
        raise TypeError(
            f"Cannot create measurement from object of type {type(x)}"
        ) from None
    return numpy.array([x]), unit


