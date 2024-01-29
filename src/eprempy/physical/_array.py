import pathlib
import typing

import matplotlib.pyplot as plt
import numpy
import numpy.typing

from .. import metric
from .. import measured
from .. import numeric
from .. import quantity
from .. import real
from ..typehelp import Self
from ._axis import Coordinates
from ._axes import Axes
from ._tensor import Tensor
from ._types import QuantityType as Q


T = typing.TypeVar('T')


class NDimError(Exception):
    """Error related to array dimension."""


class Array(Tensor[real.Array[real.ValueType]]):
    """A physical tensor with labeled axes."""

    def __init__(
        self,
        data: real.Array[real.ValueType],
        context: measured.Context[Q],
        axes: Axes,
        /,
    ) -> None:
        self._data_interface = data
        super().__init__(data, context)
        self._axes = axes
        self._scale = 1.0
        self._squeezed = None
        self._scaled = None

    def __str__(self) -> str:
        attrs = f"unit={str(self.unit)!r},\ndimensions={self.dimensions}"
        return f"{self.data.array},\n{attrs}"

    def __int__(self):
        """Called for int(self)."""
        return self._as_builtin(int)

    def __float__(self):
        """Called for float(self)."""
        return self._as_builtin(float)

    def __complex__(self):
        """Called for complex(self)."""
        return complex(float(self))

    def _as_builtin(self, t: T):
        """Convert this instance to a built-in numeric type."""
        if self.size == 1:
            return t(self.data.array.ravel()[0])
        raise TypeError(
            f"Cannot convert a size-{self.size} array to {t!r}"
        ) from None

    def __getitem__(self, args, /):
        idx = numeric.index.expand(self.ndim, args)
        data = self.data[idx]
        axes = {k: v[i] for i, (k, v) in zip(idx, self.axes.items())}
        return self.spawn(data, unit=self.unit, axes=axes)

    @typing.overload
    def transpose(
        self,
        axes: typing.Iterable[typing.Union[str, typing.SupportsIndex]],
        /,
    ) -> Self: ...

    @typing.overload
    def transpose(
        self,
        *axes: typing.Union[str, typing.SupportsIndex],
    ) -> Self: ...

    def transpose(self, *args):
        """Transpose this array."""
        if not args:
            return self
        data = self._data_interface.transpose(*args)
        axes = self.axes.permute(*args)
        return self.spawn(data, unit=self.unit, axes=axes)

    @typing.overload
    def plot(
        self,
        *args,
        x: typing.Optional[typing.Union[str, typing.Sequence]]=None,
        unit: typing.Optional[metric.UnitLike]=None,
        path: typing.Optional[pathlib.Path]=None,
        **extra
    ) -> None: ...

    def plot(self, *args, **kwargs):
        """Plot this array."""
        return plot(self, *args, **kwargs)

    @property
    def squeezed(self):
        """The equivalent `numpy` array, with singular dimensions removed."""
        if self._squeezed is None:
            self._squeezed = numpy.array(self).squeeze()
        return self._squeezed

    @property
    def data(self):
        if self._scaled is None:
            self._scaled = self._scale * self._data_interface
        return self._scaled

    @property
    def shapemap(self):
        """A mapping from dimension to axis length."""
        return self._data_interface.shapemap

    @property
    def dimensions(self):
        """This array's dimensions."""
        return self.axes.dimensions

    @property
    def axes(self) -> Axes:
        """This array's axes."""
        return self._axes

    _FUNCTIONS = {}
    _OPERATORS = {}


def converter(c: metric.Conversion, x: Array) -> Array:
    """Unit converter for physical arrays.

    Notes
    -----
    - This function differs from the unit-converter used by other `~physical`
      subclasses of `~measured.Object` by first creating an intermediate
      instance of `~Array` that contains a copy of the existing data and axes
      along with the new unit. It then updates the internal `_scale` attribute
      of the new instance so that calls to the `array` property will produce
      values consistent with the new unit.
    """
    if c.old == c.new:
        return x
    new = x.spawn(x._data_interface, unit=c.new, axes=x.axes)
    new._scale = float(c)
    return new


class AxisError(Exception):
    """Invalid plotting axis."""


_AXES_ARG_GROUPS = (
    'label',
    'lim',
    'scale',
    'bound',
    'margin',
    'ticklabels',
    'ticks',
)
_AXES_ARG_KEYS = tuple(
    [f'{q}{l}' for l in _AXES_ARG_GROUPS for q in {'x', 'y'}]
) + (
    'title',
)

def plot(
    array: Array,
    *args,
    x: typing.Optional[typing.Union[str, typing.Sequence]]=None,
    unit: typing.Optional[metric.UnitLike]=None,
    path: typing.Optional[pathlib.Path]=None,
    **extra
) -> None:
    """Plot the named array."""
    ndarray = numpy.array(array.withunit(unit or array.unit)).squeeze()
    if ndarray.ndim != 1:
        raise NDimError(f"The given array is not logically 1-D") from None
    extra['ylabel'] = f"[{array.unit.format(style='tex')}]"
    if x is None:
        dimension = next(i for i, n in array.shapemap.items() if n != 1)
        axis = array.axes[dimension]
        name = dimension.capitalize()
        if isinstance(axis, Coordinates):
            m = quantity.measure(axis)
            xarr = numpy.array(m)
            if 'xlabel' not in extra:
                extra['xlabel'] = f"{name} [{m.unit}]"
        else:
            xarr = numpy.array(axis)
            extra['xlabel'] = name
        _create_plot(xarr, ndarray, *args, **extra)
    else:
        if isinstance(x, measured.Type):
            xarr = numpy.array(x).squeeze()
        elif isinstance(x, Coordinates):
            m = quantity.measure(x)
            xarr = numpy.array(m)
            if 'xlabel' not in extra:
                extra['xlabel'] = f"{name} [{m.unit}]"
        elif isinstance(x, str):
            axis = array.axes[x]
            xarr = numpy.array(axis)
            extra['xlabel'] = x
        else:
            raise TypeError(x)
        _create_plot(xarr, ndarray, *args, **extra)
    if path is None:
        plt.show()
    else:
        plt.savefig(path)
    plt.close()


def _create_plot(*args, **extra):
    """Helper for `~plot`."""
    axes_kw = {}
    plot_kw = {}
    for key, value in extra.items():
        if key in _AXES_ARG_KEYS:
            axes_kw[key] = value
        else:
            plot_kw[key] = value
    plt.subplot(**axes_kw)
    plt.plot(*args, **plot_kw)


