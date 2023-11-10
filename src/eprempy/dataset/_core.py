import numbers
import typing

import numpy
import numpy.typing


R = typing.TypeVar('R', bound=numbers.Real)

class Member:
    """An arbitrary object from a dataset."""

    def __init__(self, **attributes) -> None:
        self._attributes = attributes
        self._strings = {}

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        these = {
            k: self._strings.get(k, v)
            for k, v in self._attributes.items()
        }
        attrs = ', '.join(f"{k}={v!r}" for k, v in these.items())
        return f"{self.__class__.__qualname__}({attrs})"


class Array(Member):
    """An array-like dataset object."""

    def __init__(
        self,
        data: numpy.typing.ArrayLike,
        unit: str,
        dimensions: typing.Tuple[str],
    ) -> None:
        super().__init__(data=data, unit=unit, dimensions=dimensions)
        self._strings['data'] = type(data)

    def __getitem__(self, index, /):
        """Called for self[index]."""
        return self.data[index]

    def __array__(self, *args, **kwargs):
        """Called for conversion to a `numpy.ndarray`."""
        array = numpy.asarray(self.data)
        return numpy.array(array, *args, **kwargs)

    @property
    def data(self) -> numpy.typing.ArrayLike:
        """The array-like data interface."""
        return self._attributes['data']

    @property
    def unit(self) -> str:
        """The metric unit of this array's data values."""
        return self._attributes['unit']

    @property
    def dimensions(self) -> typing.Tuple[str]:
        """The names of this array's axes."""
        return self._attributes['dimensions']


class Scalar(Member):
    """A scalar dataset object."""

    def __init__(self, value: R, unit: str) -> None:
        super().__init__(value=value, unit=unit)

    def __float__(self) -> float:
        """Called for float(self)."""
        return float(self.value)

    def __int__(self) -> int:
        """Called for int(self)."""
        return int(self.value)

    @property
    def value(self) -> R:
        """The value of this scalar quantity."""
        return self._attributes['value']

    @property
    def unit(self) -> str:
        """The metric unit of this scalar quantity's value."""
        return self._attributes['unit']


class Axis(Member):
    """A dataset array axis."""

    def __init__(self, size: int) -> None:
        super().__init__(size=size)

    @property
    def size(self) -> int:
        """The size of this axis."""
        return self._attributes['size']


def array_factory(
    data: numpy.typing.ArrayLike,
    unit: str,
    dimensions: typing.Iterable[str],
) -> Array:
    """Create an object representing a dataset array."""
    return Array(data, unit, tuple(dimensions))


def scalar_factory(value: R, unit: str):
    """Create an object representing a dataset scalar."""
    return Scalar(value, unit)


def axis_factory(size: int):
    """Create an object representing a dataset axis."""
    return Axis(size)


