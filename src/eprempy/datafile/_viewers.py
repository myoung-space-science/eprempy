"""
Tools for viewing the contents of an EPREM datafile.

For the purposes of this package, a datafile is a file containing simulation
output for a single observer. Each EPREM dataset contains multiple datafiles.
"""

import abc
import pathlib
import typing

import numpy.typing
import netCDF4

from .. import aliased
from .. import etc
from .. import exceptions
from .. import paths
from ._core import (
    Array,
    Scalar,
    Axis,
    array_factory,
    scalar_factory,
    axis_factory,
)
from ._reference import (
    ARRAYS,
    SCALARS,
    AXES,
)


T = typing.TypeVar('T')

class Viewer(abc.ABC):
    """An abstract base class for datafile viewers."""

    def __init__(self, source: pathlib.Path) -> None:
        self._source = source

    @abc.abstractmethod
    def get_array(self, name: str) -> Array:
        """Get the named array-like object from this datafile."""

    @abc.abstractmethod
    def get_scalar(self, name: str) -> Scalar:
        """Get the named scalar object from this datafile."""

    @abc.abstractmethod
    def get_axis(self, name: str) -> Axis:
        """Get the named array axis from this datafile."""

    @abc.abstractmethod
    def get_unit(self, name: str) -> str:
        """Get the unit for the named datafile object."""

    @property
    def source(self):
        """This datafile's source."""
        return self._source


class NetCDFViewer(Viewer):
    """A viewer for NetCDF datafiles."""

    def __init__(self, source: pathlib.Path) -> None:
        super().__init__(source)
        datafile = netCDF4.Dataset(self.source, 'r')
        self._variables = getattr(datafile, 'variables')
        self._dimensions = getattr(datafile, 'dimensions')

    def get_array(self, name: str):
        data = self._get_variable(name)
        unit = self.get_unit(name)
        dimensions = self._get_dimensions_from_data(data)
        return array_factory(data=data, unit=unit, dimensions=dimensions)

    def get_scalar(self, name: str):
        data = self._get_variable(name)
        if shape := getattr(data, 'shape', None):
            raise TypeError(
                f"Cannot convert {name!r}, with shape {shape}, to a scalar"
            ) from None
        dtype = getattr(data, 'dtype', numpy.dtype(numpy.float_))
        value = (
            int(data[:]) if numpy.issubdtype(dtype, numpy.integer)
            else float(data[:])
        )
        unit = self.get_unit(name)
        return scalar_factory(value=value, unit=unit)

    def get_axis(self, name: str):
        try:
            data = self._dimensions[name]
        except KeyError as err:
            raise KeyError(
                f"No dimension named {name!r}"
                f" in the datafile at {self.source}"
            ) from err
        size = getattr(data, 'size', None)
        return axis_factory(size=size)

    def get_unit(self, name: str) -> str:
        data = self._get_variable(name)
        return self._get_unit_from_data(data)

    def _get_variable(self, name: str):
        """Helper for retrieving datafile variables by name."""
        try:
            data = self._variables[name]
        except KeyError as err:
            raise KeyError(
                f"No variable named {name!r}"
                f" in the datafile at {self.source}"
            ) from err
        return data

    def _get_dimensions_from_data(self, data):
        """Compute appropriate variable dimensions from a datafile object."""
        return tuple(getattr(data, 'dimensions', ()))

    def _get_unit_from_data(self, data):
        """Compute appropriate variable units from a datafile object."""
        available = (
            getattr(data, attr) for attr in ('unit', 'units')
            if hasattr(data, attr)
        )
        return next(available, None)


HINTS = {
    '.nc': ['netcdf', 'NetCDF', 'NETCDF'],
}
"""Non-suffix aliases for datafile file types."""


_viewers = {
    '.nc': NetCDFViewer,
}
VIEWERS = aliased.Mapping(_viewers, aliases=HINTS)
"""The available datafile-viewing classes."""


@etc.autostr
class View(metaclass=paths.PathSet):
    """A format-agnostic view of a datafile.

    An instance of this class provides access to variables and axes defined in a
    specific datafile, given a path to that datafile. It is designed to provide
    a single interface, regardless of file type, with as little overhead as
    possible. Therefore, it does not attempt to modify attributes (e.g.,
    converting variable units), since doing so could result in reading a
    potentially large array from disk.
    """

    def __init__(
        self,
        source: pathlib.Path,
        hint: typing.Optional[str],
    ) -> None:
        self._source = source
        self._hint = hint
        self._viewer = None
        self._arrays = None
        self._scalars = None
        self._sizes = None
        self._axes = None
        self._units = None

    def __str__(self) -> str:
        return str(self.source)

    @typing.overload
    def __getitem__(
        self,
        key: typing.Literal['arrays'],
    ) -> typing.Dict[str, Array]: ...

    @typing.overload
    def __getitem__(
        self,
        key: typing.Literal['scalars'],
    ) -> typing.Dict[str, Scalar]: ...

    @typing.overload
    def __getitem__(
        self,
        key: typing.Literal['axes'],
    ) -> typing.Dict[str, Axis]: ...

    def __getitem__(self, __k):
        """Access properties by name."""
        try:
            this = getattr(self, __k)
        except AttributeError as err:
            raise KeyError(
                f"{self.__class__} has no property named {__k!r}"
            ) from err
        return this

    @property
    def units(self):
        """The unit of each datafile quantity, if available."""
        if self._units is None:
            reference = list(ARRAYS) + list(SCALARS)
            self._units = self._map(self.viewer.get_unit, reference)
        return self._units

    @property
    def arrays(self):
        """The array-like quantities in this datafile."""
        if self._arrays is None:
            self._arrays = self._map(self.viewer.get_array, ARRAYS)
        return self._arrays

    @property
    def scalars(self):
        """The scalar quantities in this datafile."""
        if self._scalars is None:
            self._scalars = self._map(self.viewer.get_scalar, SCALARS)
        return self._scalars

    @property
    def sizes(self):
        """The length of each datafile dimension."""
        if self._sizes is None:
            self._sizes = {k: v.size for k, v in self.axes.items()}
        return self._sizes

    @property
    def axes(self):
        """The array-axis quantities in this datafile."""
        if self._axes is None:
            self._axes = self._map(self.viewer.get_axis, AXES)
        return self._axes

    def _map(
        self,
        get: typing.Callable[[str], T],
        reference: typing.Iterable[str],
    ) -> typing.Dict[str, T]:
        """Create a mapping of datafile attributes."""
        guarded = exceptions.Wrapper(get)
        guarded.catch(KeyError)
        mapped = {k: guarded.compute(k) for k in reference}
        return {k: v for k, v in mapped.items() if v is not None}

    @property
    def viewer(self) -> Viewer:
        """The appropriate file viewer for this datafile."""
        if self._viewer is None:
            try:
                viewer = VIEWERS[self.source.suffix]
            except KeyError:
                viewer = VIEWERS.get(self._hint)
            self._viewer = viewer(self.source)
        return self._viewer

    @property
    def source(self):
        """The file containing output data."""
        return self._source


def view_factory(
    source: paths.PathLike,
    *,
    hint: typing.Optional[str]=None,
) -> View:
    """Create a format-agnostic view of an EPREM datafile.

    Parameters
    ----------
    source : string or `os.PathLike`
        The path to the target datafile. The path must exist. This function will
        convert `source` into a fully qualified `pathlib.Path`.
    hint : optional; keyword only
        A defined alias for the target file type. See Notes for further
        explanation.

    Notes
    -----
    - The datafile-viewing interface will attempt to determine the correct
      file-type viewer for the target datafile based on the path suffix.
      Providing a `hint` allows the interface to choose the appropriate viewer
      even in cases when the target file does not have the expected suffix.
    """
    return View(paths.fullpath(source, strict=True), hint=hint)


