import builtins
import contextlib
import numbers
import operator as standard
import typing

import numpy
import numpy.typing
from scipy.interpolate import interp1d

from .. import aliased
from .. import container
from .. import datafile
from .. import etc
from .. import measured
from .. import metric
from .. import numeric
from .. import parameter
from .. import physical
from .. import quantity
from .. import reference
from ..reference import ARRAYS
from ..typehelp import Self


class Interpolant(typing.NamedTuple):
    """Attributes necessary for interpolation."""
    reference: physical.Array
    targets: numpy.ndarray


class Array(physical.Array):
    """A physical array with interpolation support."""

    def interpolate(
        self: Self,
        interpolants: typing.Mapping[str, Interpolant],
    ) -> Self:
        """Interpolate this array to target values."""
        return interpolate(self, interpolants)


def array_factory(x, **kwargs):
    """Create an observable array."""
    if isinstance(x, physical.Array):
        return Array(x.data, x.context, x.axes)
    return physical.array(x, **kwargs)


def interpolate(
    array: physical.Array,
    interpolants: typing.Mapping[str, Interpolant],
) -> Array:
    """Interpolate a physical array.

    Parameters
    ----------
    array : `~Array`
        The array object to interpolate.

    interpolants : mapping from string to `~Interpolant`
    """
    if not interpolants:
        # If there are no interpolants, return the array as-is. This is simply a
        # convenience so that calling code need not check whether `interpolants`
        # is empty before calling this function.
        return array
    workspace = None
    axes = array.axes.copy()
    for dimension, interpolant in interpolants.items():
        workspace = _update_interpolation(
            array,
            interpolant.reference,
            interpolant.targets,
            workspace=workspace,
        )
        s = measured.sequence(interpolant.targets, interpolant.reference.unit)
        if dimension in ARRAYS.aliases['radius']:
            axes = axes.replace('shell', radius=physical.Coordinates(s))
        else:
            axes = axes.replace(dimension, physical.Coordinates(s))
    return array.spawn(workspace, unit=array.unit, axes=axes)


def _update_interpolation(
    array: Array,
    reference: numeric.Array,
    targets: numpy.ndarray,
    workspace: numpy.ndarray=None,
) -> numpy.ndarray:
    """Helper for `~interpolate`."""
    x = numpy.array(array) if workspace is None else workspace
    indices = (array.dimensions.index(d) for d in reference.dimensions)
    dst, src = zip(*enumerate(indices))
    reordered = numpy.moveaxis(x, src, dst)
    interpolated = _apply_interpolation(reordered, reference, targets)
    return numpy.moveaxis(interpolated, dst, src)


def _apply_interpolation(
    data: numpy.typing.ArrayLike,
    reference: numpy.typing.ArrayLike,
    targets: typing.Iterable[float],
) -> numpy.ndarray:
    """Interpolate `data` to target values with respect to `reference`.

    This function will always interpolate over the leading dimension.

    Parameters
    ----------
    data : array-like
        The array-like object to interpolate. This function will convert `data`
        to a `numpy.ndarray`.

    reference : array-like
        The values at which `data` is known. This function will convert
        `reference` to a `numpy.ndarray`.

    targets : iterable of float
        The value(s) to which to interpolate `data`.

    Returns
    -------
    `numpy.ndarray`
        An array with the same shape as `array`, except for the interpolated
        dimension, which will have the same length as the number of values
        `targets`.
    """
    darray = numpy.array(data)
    rarray = numpy.array(reference)
    interpolated = [
        _apply_interp1d(darray, rarray, target)
        for target in targets
    ]
    if rarray.ndim == 2:
        return numpy.swapaxes(interpolated, 0, 1)
    return numpy.array(interpolated)


def _apply_interp1d(
    array: numpy.ndarray,
    reference: numpy.ndarray,
    target: float,
) -> typing.List[float]:
    """Interpolate data to `target` along the leading axis."""
    if target in reference:
        idx = container.nearest(reference, target).index
        return array[idx]
    ndim = reference.ndim
    if ndim == 2:
        interps = [interp1d(x, y, axis=0) for x, y in zip(reference, array)]
        return numpy.array([interp(target) for interp in interps])
    if ndim != 1:
        raise physical._array.NDimError(
            f"The reference array may have 1 or 2 (not {ndim}) dimensions"
        ) from None
    if reference.size == 1:
        # This works because we are interpolating over the leading dimension by
        # definition. Squeezing does not necessarily work because there may be
        # other singular dimensions.
        return array[0]
    interp = interp1d(reference, array, axis=0)
    return interp(target)


class Arguments(aliased.Mapping[str, measured.Object]):
    """Array indices and physical assumptions."""

    def __init__(
        self,
        indices: typing.Dict[str, numeric.index.Sequence],
        **assumptions: measured.Object
    ) -> None:
        aliases = reference.ALIASES | parameter.ALIASES
        super().__init__(assumptions, aliases=aliases)
        self._time = indices.get('time')
        self._shell = indices.get('shell')
        self._species = indices.get('species')
        self._energy = indices.get('energy')
        self._mu = indices.get('mu')
        self._extra = assumptions
        self._indices = None
        self._assumptions = None

    def axes(
        self,
        optional: typing.Iterable[str]=None,
        **extra
    ) -> typing.Dict[str, physical.AxisType]:
        """Build a mapping of indices and pseudo indices.
        
        Parameters
        ----------
        optional : iterable of string, optional
            Zero or more names of arguments to include if they are available.

        **extra
            Zero or more key-value pairs in which the key is an argument name
            and the value is the default value to include if the argument is not
            available.

        Notes
        -----
        - In some cases, the mere presence of a parameter may trigger a certain
          algorithmic path (e.g., interpolation) whereas some cases may require
          a particular argument, then proceed depending on the value. Requesting
          an argument via `optional` is more appropriate for the former while
          requesting an argument via `**extra` is more appropriate for the
          latter.
        """
        indices = self.indices.copy()
        for key in optional or ():
            with contextlib.suppress(KeyError):
                indices[key] = self[key]
        for key, default in extra.items():
            indices[key] = self.get(key, default)
        return indices

    @property
    def assumptions(self):
        """All non-index attributes."""
        if self._assumptions is None:
            assumptions = {
                k: v
                if isinstance(v, (physical.Scalar, physical.Tensor, slice))
                else parameter.variable(quantity.measure(v))
                for k, v in self._extra.items()
            }
            aliases = reference.ALIASES | parameter.ALIASES
            self._assumptions = aliased.Mapping(assumptions, aliases=aliases)
        return self._assumptions

    @property
    def indices(self):
        """All axis indices as a mapping."""
        if self._indices is None:
            self._indices = {
                'time': self.time,
                'shell': self.shell,
                'species': self.species,
                'energy': self.energy,
                'mu': self.mu,
            }
        return self._indices

    @property
    def time(self):
        """The time-dimension index."""
        return self._time

    @property
    def shell(self):
        """The shell-dimension index."""
        return self._shell

    @property
    def species(self):
        """The species-dimension index."""
        return self._species

    @property
    def energy(self):
        """The energy-dimension index."""
        return self._energy

    @property
    def mu(self):
        """The mu-dimension index."""
        return self._mu

    def __str__(self) -> str:
        parts = [f"{k}: {getattr(self, k)}" for k in datafile.AXES]
        if s := super().__str__():
            parts.append(s)
        return ', '.join(parts)


class ArgumentError(Exception):
    """Unknown or invalid argument."""


class Context:
    """A general observing context."""

    def __init__(
        self,
        operator: typing.Callable[[Arguments], physical.Array],
        axes: datafile.Axes,
        grid: datafile.Grid,
    ) -> None:
        """Initialize this context."""
        self._operator = operator
        self._axes = axes
        self._grid = grid

    def __eq__(self, other) -> bool:
        """Called for self == other."""
        return (
            isinstance(other, Context)
            and
            self.axes == other.axes
            and
            self.operator == other.operator
        )

    def apply(self, arg: Arguments) -> physical.Array:
        """Apply the observing operation to existing arguments."""
        return self.operator(arg)

    def implement(self, **user) -> physical.Array:
        """Implement the observing operation within this context."""
        # NOTE: This method should assume for now that `user` contains all the
        # necessary axis indices for the target quantity. That is a reasonable
        # assumption whenever `Operation.__getitem__` calls this method, which
        # is currently the only use case.
        indexed = {}
        parsed = {}
        for k, v in user.items():
            try:
                p = self._parse_user_arg(k, v)
            except physical.AxisValueError:
                # NOTE: We are here because `k` is the name of an axis but `v`
                # is not a value in the corresponding axis array. We will
                # therefore indicate to downstream code that it needs to
                # interpolate the corresponding axis to `v` by storing `v` as an
                # assumption and storing a full slice as the relevant index.
                indexed[k] = self._parse_user_arg(k, slice(None))
                parsed[k] = self._parse_user_arg('', v)
            else:
                if k in self.axes:
                    indexed[k] = p
                else:
                    parsed[k] = p
        for key in {'time', 'energy', 'mu'}:
            if key in parsed:
                x = self.axes[key]
                v = parsed[key].withunit(x.unit)
                w = (float(i) for i in v)
                idx = numeric.index.restrict(x, *w, axis=0)
                indexed[key] = numeric.index.sequence(idx)
        if 'radius' in parsed:
            x = self.grid.r
            rv = parsed['radius'].withunit(x.unit)
            rs = (float(ri) for ri in rv)
            idx = numeric.index.restrict(x, *rs, axis=1)
            indexed['shell'] = numeric.index.sequence(idx)
        return self.operator(Arguments(indices=indexed, **parsed))

    def _parse_user_arg(self, k: str, v):
        """Convert a given argument into the appropriate object."""
        if quantity.isindexlike(v):
            return numeric.index.sequence(v)
        name = reference.AXES.names.get(k, k)
        if name in self.axes:
            axis = self.axes[name]
            if isinstance(v, slice):
                return axis.indices[v]
            return axis.index(v)
        # At this point, we can be reasonably confident that `v` is not an axis
        # index, so we will treat it as a physical assumption.
        if isinstance(v, slice):
            return v
        with contextlib.suppress(quantity.MeasuringTypeError):
            return quantity.measure(v)
        raise ArgumentError(
            f"Argument {k!r} is either unknown or has invalid type"
        ) from None

    @property
    def operator(self):
        """The observing function."""
        return self._operator

    @property
    def axes(self):
        """The array-indexing objects."""
        return self._axes

    @property
    def grid(self):
        """The coordinate arrays."""
        return self._grid


class ObservationError(Exception):
    """There is an error in the observed array."""


class Quantity:
    """An arbitrary observable quantity with an array-like interface."""

    def __init__(
        self,
        context: Context,
        unit: metric.Unit,
        dimensions: numeric.Dimensions,
    ) -> None:
        self._context = context
        self._unit = unit
        self._dimensions = dimensions
        self._ndim = None

    def __repr__(self) -> str:
        """A simplified representation of this object."""
        _str = f"unit={str(self.unit)!r}, dimensions={self.dimensions}"
        return f"{self.__class__.__qualname__}({_str})"

    def __array__(self, *args, **kwargs):
        """Called for conversion to a `numpy.ndarray`.

        Notes
        -----
        - All arguments pass directly to the `numpy` array constructor.
        - This will create an array from the entire observable quantity. If you
          want to create an array from a subset of the observable data, you must
          first subscript this quantity, then call `numpy.array` on the result.
          In fact, this method is simply a convenient shorthand for that
          processes, in the case when the subscription returns the full array.
        """
        return numpy.array(self[:], *args, **kwargs)

    def __getitem__(self, args):
        """Access observable data via array subscription."""
        # If `args` is an instance of `Arguments`, we are computing an
        # intermediate quantity. Therefore, we have already been through the
        # normalization process and we simply want to pass the existing set of
        # arguments along to the target operator.
        if isinstance(args, Arguments):
            return self.context.apply(args)
        # Expand arguments to one index per dimension.
        normalized = self._normalize(args)
        nargs = len(normalized)
        ndims = len(self.dimensions)
        if nargs != ndims:
            raise IndexError(
                f"Number of indices ({nargs})"
                f" != number of dimensions ({ndims})"
            ) from None
        # Map each given index to its dimension.
        mapped = dict(zip(self.dimensions, normalized))
        axes = {k: v for k, v in mapped.items() if k != 'shell'}
        # Sort out the 'shell'/'radius' index. NOTE: If 'shell' is not in
        # self.dimensions, should we immediately return?
        if 'shell' in mapped:
            key, value = self._shell_or_radius(mapped)
            axes[key] = value
        # Implement this operation within the observing context. NOTE: The
        # design philosophy here assumes that each operator knows best how to
        # implement common array-manipulation tasks (e.g., interpolation). One
        # problem with that strategy is that the implementation step will raise
        # a `ValueError` before the operator has a chance to interpolate if a
        # physical axis value is not in the corresponding instance of
        # `Coordinates`.
        result = self.context.implement(**axes)
        # Check for unit consistency.
        if result.unit | self.unit:
            return result.withunit(self.unit)
        raise ObservationError(
            f"The unit of the observed array ({str(result.unit)!r})"
            f" is not consistent with the expected unit ({str(self.unit)!r})"
        ) from None

    def _normalize(self, args):
        """Observable-specific index normalization."""
        if self.ndim == 1 and quantity.ismeasurable(args):
            return numeric.index.expand(self.ndim, [args])
        return numeric.index.expand(self.ndim, args)

    def _shell_or_radius(self, axes: dict):
        """Determine whether the shell axis represents a radius."""
        shell = axes.get('shell', slice(None))
        if isinstance(shell, slice):
            return 'shell', shell
        s = quantity.measure(shell)
        if not quantity.isindexlike(s) and s.unit.quantity == 'length':
            return 'radius', physical.coordinates(s)
        return 'shell', physical.points(numpy.array(s))

    def __eq__(self, other):
        """Called for self == other."""
        return (
            isinstance(other, Quantity)
            and
            not self._unequal_metadata(other)
            and
            self.context == other.context
        )

    def __add__(self, other):
        """Called for self + other."""
        if not isinstance(other, Quantity):
            return NotImplemented
        if found := self._unequal_metadata(other):
            attrs = etc.join(found, quoted=True)
            raise ValueError(
                f"Cannot add quantities with unequal values of {attrs}"
            ) from None
        return self._apply(
            standard.add,
            other,
            self.unit,
            self.dimensions,
        )

    def __sub__(self, other):
        """Called for self - other."""
        if not isinstance(other, Quantity):
            return NotImplemented
        if found := self._unequal_metadata(other):
            attrs = etc.join(found, quoted=True)
            raise ValueError(
                f"Cannot subtract quantities with unequal values of {attrs}"
            ) from None
        return self._apply(
            standard.sub,
            other,
            self.unit,
            self.dimensions,
        )

    def __mul__(self, other):
        """Called for self * other."""
        if not isinstance(other, Quantity):
            return NotImplemented
        unit = self.unit * other.unit
        dimensions = self.dimensions | other.dimensions
        return self._apply(standard.mul, other, unit, dimensions)

    def __truediv__(self, other):
        """Called for self / other."""
        if not isinstance(other, Quantity):
            return NotImplemented
        unit = self.unit / other.unit
        dimensions = self.dimensions | other.dimensions
        return self._apply(standard.truediv, other, unit, dimensions)

    def __pow__(self, other):
        """Called for self ** other."""
        if not isinstance(other, numbers.Real):
            return NotImplemented
        unit = self.unit ** other
        return self._apply(
            builtins.pow,
            other,
            unit,
            self.dimensions,
        )

    def _unequal_metadata(self, other):
        """Return names of unequal metadata attributes."""
        if not isinstance(other, Quantity):
            raise TypeError(other)
        attrs = {'unit', 'dimensions'}
        unequal = [
            attr for attr in attrs
            if getattr(self, attr) != getattr(other, attr)
        ]
        return tuple(unequal)

    def _apply(self, operator, other, *attrs):
        """Apply a standard algebraic operator."""
        def __f(user: Arguments):
            return operator(self[user], other[user])
        context = Context(__f, self.context.axes, self.context.grid)
        return Quantity(context, *attrs)

    def withunit(self, new: metric.UnitLike, /):
        """Convert this quantity to a new unit."""
        if self.unit == new:
            return self
        if self.unit | new:
            unit = metric.unit(new)
            return Quantity(self.context, unit, self.dimensions)
        raise ValueError(
            f"The unit {str(new)!r} is inconsistent"
            f" with {str(self.unit)!r}"
        ) from None

    @property
    def context(self):
        """The relevant observing context."""
        return self._context

    @property
    def ndim(self):
        """The number of indexable dimensions."""
        if self._ndim is None:
            self._ndim = len(self.dimensions)
        return self._ndim

    @property
    def unit(self):
        """The metric unit of this quantity."""
        return self._unit

    @property
    def dimensions(self):
        """The indexable dimensions of this quantity."""
        return self._dimensions


