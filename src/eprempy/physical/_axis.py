"""
Support for defining and working with physical array axes.
"""

import contextlib
import numbers
import typing

import numpy
import numpy.typing

from .. import container
from .. import etc
from .. import measured
from .. import metric
from .. import numeric
from .. import quantity
from ..typehelp import Self


T = typing.TypeVar('T')


class AxisValueError(ValueError):
    """Error in axis argument value."""


class AxisTypeError(TypeError):
    """Error in axis argument type."""


@etc.autostr
class Axis(numeric.Object[T]):
    """A generalized array axis."""

    def __init__(self, reference: T) -> None:
        super().__init__(reference)
        self._indices = None
        self._length = None

    def index(self, *targets: T):
        """Compute appropriate axis indices."""
        indices = self.normalize(*targets)
        if not all(isinstance(arg, numbers.Integral) for arg in indices):
            raise TypeError(
                f"Not all target indices have integral type: {targets}"
            ) from None
        if index := self._out_of_bounds(indices):
            raise ValueError(
                f"Index {index} is out of bounds for axis"
                f" with size {len(self)}"
            ) from None
        if len(indices) == 1:
            index = indices[0]
            with contextlib.suppress(TypeError):
                return numeric.index.value(int(index))
        return numeric.index.sequence(indices)

    def normalize(self, *targets: T):
        if not targets:
            return range(len(self))
        if len(targets) == 1:
            target = targets[0]
            if isinstance(target, slice):
                return container.slice2range(target, stop=len(self))
            if isinstance(target, (list, tuple, numpy.ndarray)):
                return target
            if container.isiterable(target):
                return list(target)
            # If `targets` is a tuple with a single member at this point,
            # execution will fall through and the function will return a list
            # containing only that element.
        return list(targets)

    def _out_of_bounds(self, indices: typing.Iterable[typing.SupportsIndex]):
        """Return the first index outside the bounds of this axis."""
        for index in indices:
            if index < -len(self) or index > len(self)-1:
                return index

    def __contains__(self, __x):
        """Called for x in self."""
        if isinstance(__x, Axis) and len(__x) == 1:
            with contextlib.suppress(Exception):
                return self.index(__x) in self.indices
        return __x in self.data

    def __getitem__(self, __i):
        """Called for index-based access.

        This method will generate a new instance of the appropriate (sub)class
        from its reference array. If `__i` is not `:` or `...`, this method will
        populate the internal `_indices` attribute with the indices
        corresponding to `__i`. Otherwise, it will immediately return the new
        axis object, which will automatically populate `_indices` as necessary.
        Both cases are designed to preserve index information with regard to the
        original reference array.
        """
        axis = self.spawn(self.data[__i])
        if __i in (slice(None), ...):
            return axis
        idx = self.normalize(container.unwrap(__i))
        axis._indices = numeric.index.sequence(idx)
        return axis

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.data)

    def __iter__(self):
        """Called for iter(self)."""
        return iter(self.data)

    def __eq__(self, other):
        """Called for self == other."""
        if isinstance(other, Axis):
            return numpy.array_equal(self.data, other.data)
        return NotImplemented

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
        return f"{prefix}{data}{suffix}"

    def _format_data(self, **kwargs):
        """Create an appropriate string to represent the data."""
        array = numpy.array(self.data)
        try:
            signed = '+' if any(i < 0 for i in array.flat) else '-'
        except TypeError:
            # If we get here, it's probably because some values are strings
            signed = '-'
        return numpy.array2string(
            array,
            threshold=4,
            edgeitems=2,
            separator=', ',
            sign=signed,
            precision=3,
            floatmode='maxprec_equal',
            **kwargs
        )

    @property
    def indices(self) -> numeric.index.Sequence:
        """The corresponding index sequence."""
        if self._indices is None:
            self._indices = numeric.index.sequence(range(self.length))
        return self._indices

    @property
    def length(self) -> int:
        """The number of values in this axis."""
        if self._length is None:
            self._length = len(self.data)
        return self._length


AxisLike = typing.TypeVar('AxisLike', typing.Iterable[str], Axis)


class Points(Axis[numpy.typing.NDArray[numpy.uint]]):
    """The interface to an integral axis."""

    def __init__(self, data: numpy.typing.NDArray[numpy.uint]) -> None:
        super().__init__(data)

    def index(self, *targets: T):
        if not targets:
            return self.indices
        points = self.normalize(*targets)
        indices = []
        for point in points:
            if point not in self.data:
                raise AxisValueError(
                    f"This axis does not contain the point {point}"
                ) from None
            index = numpy.where(self.data == point)
            indices.append(index[0][0])
        if len(indices) == 1:
            return numeric.index.value(indices[0])
        return numeric.index.sequence(indices)

    @property
    def indices(self):
        if self._indices is None:
            self._indices = numeric.index.sequence(self.data)
        return self._indices


class Symbols(Axis[typing.List[str]]):
    """The interface to a symbolic axis."""

    def __init__(self, data: typing.List[str]) -> None:
        super().__init__(data)

    def __getitem__(self, index, /):
        if container.isiterable(index):
            return self.spawn([self.data[i] for i in index])
        return super().__getitem__(index)

    def index(self, *targets: T):
        if not targets:
            return self.indices
        if not all(isinstance(target, str) for target in targets):
            raise AxisTypeError(
                "All index targets must be strings"
            ) from None
        indices = [
            self.data.index(str(target))
            for target in targets
        ]
        if len(indices) == 1:
            return numeric.index.value(indices[0])
        return numeric.index.sequence(indices)


class Coordinates(Axis[measured.Sequence[numbers.Real]]):
    """The interface to a measured axis."""

    def __init__(self, data: measured.Sequence[numbers.Real]) -> None:
        super().__init__(data)

    def index(
        self,
        *targets: typing.Union[numbers.Real, str],
        closest: typing.Optional[str]=None,
    ) -> typing.Union[numeric.index.Value, numeric.index.Sequence]:
        if not targets:
            return self.indices
        this = self._measure(targets)
        if not this:
            raise AxisTypeError(f"Cannot measure {targets}") from None
        # At this point, we can assume that `this` is a measurement that we can
        # use to compute the indices of the target values. First, we need to
        # convert the measured values into the unit of this axis. That
        # conversion is straightfoward unless `targets` comprises only numbers,
        # in which case `this` will be unitless. In that case, we assume that
        # the caller meant to imply the use of the current unit (which may
        # actually be '1') and we therefore need to assign the current unit to
        # the measured values rather than convert them to the current unit.
        # - Cases:
        #   - targets are all numbers
        #     - the implicit unit is '1': We need to assign the current unit.
        #   - targets include a unit
        #     - the explicit unit is equivalent to the current unit: No change
        #       is necessary.
        #     - the explicit unit is not equivalent to the current unit: We need
        #       to convert them to the current unit.
        #     - the explicit unit is inconsistent with the current unit: This
        #       will raise an exception during conversion.
        #
        # Rather than separately handling each case, this method explicitly
        # assigns the measured unit to the measured value unless the measured
        # unit is '1', in which case it explicitly assigns the current unit. It
        # then explicitly converts the result to the current unit.
        # - Thus
        #   - if the target unit is implicitly '1' and the current unit is also
        #     '1', we will end up re-assigning the correct unit to the measured
        #     values at the cost of creating an intermediate sequence object,
        #     but the subsequent conversion to the current unit will be a no-op
        #   - if the target unit is implicitly '1' and the current unit is not
        #     '1', we will correctly assign the current unit to the measured
        #     values and the subsequence conversion to the current unit will be
        #     a no-op
        #   - if the targets have an explicit unit, we will end up re-assigning
        #     that unit to the measured values at the cost of creating an
        #     intermediate sequence object before converting the measured values
        #     to the current unit
        #
        # - Determine the most appropriate unit.
        unit = this.unit if this.unit != '1' else self.unit
        # - Create a temporary sequence with the intermediate unit. The
        #   following line casts `this` to a `numpy.ndarray` in order to force
        #   the unit update.
        tmp = measured.sequence(numpy.array(this), unit=unit)
        # - Convert the temporary array to this coordinate's unit and extract a
        #   numpy array. If the unit of `targets` is inconsistent with our unit,
        #   this is when we'll find out.
        array = numpy.array(tmp.withunit(self.unit))
        # - Convert target values to indices in the reference array. This will
        #   first make sure each target is close enough to a value in the
        #   reference array to be considered "in" the array. That check is
        #   important because `container.nearest` will naively find the
        #   numerically closest value, which may not be useful. It also lets
        #   calling code determine how to handle values not contained in the
        #   reference array (e.g., by interpolation or extrapolation).
        indices = [self._compute_index(target, closest) for target in array]
        if len(indices) == 1:
            return numeric.index.value(indices[0])
        return numeric.index.sequence(indices)

    def _compute_index(self, target, closest):
        """Helper for `index`."""
        if numeric.data.isclose(self.data, target):
            return container.nearest(self.data, target).index
        if closest is None:
            raise AxisValueError(
                f"{self.data} does not contain {target}"
            ) from None
        if closest == 'lower':
            return container.nearest(self.data, target, 'upper').index
        if closest == 'upper':
            return container.nearest(self.data, target, 'lower').index
        raise ValueError(f"Unknown constraint {closest!r}") from None

    def _measure(self, targets: typing.Sequence):
        """Create a measured sequence, if possible."""
        if len(targets) == 1:
            target = targets[0]
            if quantity.ismeasurable(target):
                return quantity.measure(target)
        with contextlib.suppress(quantity.ParsingTypeError):
            return quantity.measure(targets)

    def __eq__(self, other):
        if isinstance(other, Coordinates):
            return super().__eq__(other) and self.unit == other.unit
        return super().__eq__(other)

    def __measure__(self) -> quantity.Measurement:
        """Called for `~quantity.measure(self)`."""
        return quantity.measurement(self.data)

    def withunit(self: Self, new: metric.UnitLike, /) -> Self:
        """Convert this cooridinate to a new unit."""
        s = self.data.withunit(new)
        return self.spawn(s)

    @property
    def unit(self):
        """The metric unit of reference values."""
        return self.data.unit


