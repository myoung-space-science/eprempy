import pathlib
import typing

import numpy.typing

from .. import atomic
from .. import etc
from .. import metric
from .. import paths
from .. import physical
from ._reference import AXES
from ._viewers import view_factory


@etc.autostr
class Axes(typing.Mapping[str, physical.Axis]):
    """A interface to the canonical array axes."""

    def __init__(
        self,
        source: pathlib.Path,
        system: metric.System,
    ) -> None:
        """Initialize this interface."""
        self._source = source
        self._system = system
        self._view = None
        self._time = None
        self._shell = None
        self._species = None
        self._energy = None
        self._mu = None

    @typing.overload
    def __getitem__(
        self,
        __k: typing.Literal['time'],
    ) -> physical.Coordinates: ...

    @typing.overload
    def __getitem__(
        self,
        __k: typing.Literal['shell'],
    ) -> physical.Points: ...

    @typing.overload
    def __getitem__(
        self,
        __k: typing.Literal['species'],
    ) -> physical.Symbols: ...

    @typing.overload
    def __getitem__(
        self,
        __k: typing.Literal['energy'],
    ) -> physical.Coordinates: ...

    @typing.overload
    def __getitem__(
        self,
        __k: typing.Literal['mu'],
    ) -> physical.Coordinates: ...

    @typing.overload
    def __getitem__(self, __k: str) -> physical.Axis: ...

    def __getitem__(self, __k: str):
        """Called for key-based access."""
        try:
            axis = getattr(self, __k)
        except AttributeError as err:
            raise KeyError(
                f"No axis named {__k!r} in {self.view!r}"
            ) from err
        return axis

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(AXES)

    def __iter__(self) -> typing.Iterator[str]:
        """Called for iter(self)."""
        return iter(AXES)

    @property
    def time(self):
        """The output times."""
        if self._time is None:
            data = self._create('time')
            self._time = physical.coordinates(data)
        return self._time

    @property
    def shell(self):
        """The simulation node layers."""
        if self._shell is None:
            data = self.view.arrays['shell'].data
            self._shell = physical.points(data)
        return self._shell

    @property
    def species(self):
        """The energetic-particle species."""
        if self._species is None:
            mass = self._create('mass', unit='nuc')
            charge = self._create('charge', unit='e')
            data = atomic.elements(mass=mass, charge=charge)
            self._species = physical.symbols(data)
        return self._species

    @property
    def energy(self) -> physical.Array:
        """The particle energies."""
        if self._energy is None:
            data = numpy.squeeze(self._create('egrid'))
            self._energy = physical.coordinates(data)
        return self._energy

    @property
    def mu(self):
        """The particle pitch-angle cosines."""
        if self._mu is None:
            data = self._create('mu')
            self._mu = physical.coordinates(data)
        return self._mu

    def _create(
        self,
        name: str,
        unit: metric.UnitLike=None,
    ) -> physical.Tensor:
        """Create an array for the named quantity."""
        try:
            base = self.view.arrays[name]
        except KeyError as err:
            raise KeyError(f"No quantity {name!r} in {self.view!r}") from err
        array = physical.tensor(
            numpy.array(base.data),
            unit=metric.standardize(base.unit),
        )
        return array.withunit(unit or str(self.system))

    @property
    def view(self):
        """A view into this dataset on disk."""
        if self._view is None:
            self._view = view_factory(self.source)
        return self._view
    
    @property
    def source(self):
        """This dataset's source path."""
        return self._source

    @property
    def system(self):
        """The metric system in which to represent this dataset."""
        return self._system


@etc.autostr
class Arrays:
    """An interface to array-like quantities in a fixed metric system."""

    def __init__(
        self,
        source: pathlib.Path,
        system: metric.System,
    ) -> None:
        """Initialize this interface."""
        self._source = source
        self._system = system
        self._axes = None
        self._view = None
        self._time = None
        self._shell = None
        self._species = None
        self._energy = None
        self._mu = None
        self._v = None
        self._mass = None
        self._charge = None
        self._r = None
        self._theta = None
        self._phi = None
        self._br = None
        self._btheta = None
        self._bphi = None
        self._ur = None
        self._utheta = None
        self._uphi = None
        self._rho = None
        self._f = None
        self._flux = None
        self._hasdist = None
        self._hasflux = None

    @property
    def time(self):
        """The output times."""
        if self._time is None:
            self._time = self._create('time')
        return self._time

    @property
    def shell(self):
        """The simulation node layers."""
        if self._shell is None:
            self._shell = self.view.arrays['shell'].data
        return self._shell

    @property
    def species(self):
        """The energetic-particle species."""
        if self._species is None:
            mass = self._create('mass', unit='nuc')
            charge = self._create('charge', unit='e')
            self._species = atomic.elements(mass=mass, charge=charge)
        return self._species

    @property
    def energy(self) -> physical.Array:
        """The particle energies."""
        if self._energy is None:
            self._energy = numpy.squeeze(self._create('egrid'))
        return self._energy

    @property
    def v(self) -> physical.Array:
        """The particle speeds."""
        if self._v is None:
            self._v = numpy.squeeze(self._create('vgrid'))
        return self._v

    @property
    def mu(self):
        """The particle pitch-angle cosines."""
        if self._mu is None:
            self._mu = self._create('mu')
        return self._mu

    @property
    def mass(self):
        """The mass of each species."""
        if self._mass is None:
            self._mass = self._create('mass', unit=self.system['mass'].unit)
        return self._mass

    @property
    def charge(self):
        """The charge of each species."""
        if self._charge is None:
            self._charge = self._create(
                'charge',
                unit=self.system['charge'].unit,
            )
        return self._charge

    @property
    def r(self):
        """The radial observer coordinates."""
        if self._r is None:
            self._r = self._create('R')
        return self._r

    @property
    def theta(self):
        """The polar observer coordinates."""
        if self._theta is None:
            self._theta = self._create('T')
        return self._theta

    @property
    def phi(self):
        """The azimuthal observer coordinates."""
        if self._phi is None:
            self._phi = self._create('P')
        return self._phi

    @property
    def br(self):
        """The magnetic-field radial component."""
        if self._br is None:
            self._br = self._create('Br')
        return self._br

    @property
    def btheta(self):
        """The magnetic-field polar component."""
        if self._btheta is None:
            self._btheta = self._create('Bt')
        return self._btheta

    @property
    def bphi(self):
        """The magnetic-field polar component."""
        if self._bphi is None:
            self._bphi = self._create('Bp')
        return self._bphi

    @property
    def ur(self):
        """The velocity-field radial component."""
        if self._ur is None:
            self._ur = self._create('Vr')
        return self._ur

    @property
    def utheta(self):
        """The velocity-field polar component."""
        if self._utheta is None:
            self._utheta = self._create('Vt')
        return self._utheta

    @property
    def uphi(self):
        """The velocity-field polar component."""
        if self._uphi is None:
            self._uphi = self._create('Vp')
        return self._uphi

    @property
    def rho(self):
        """The plasma density."""
        if self._rho is None:
            self._rho = self._create('Rho')
        return self._rho

    @property
    def f(self):
        """The particle distribution."""
        if self._f is None:
            if not self.hasflux:
                self._f = self._create('Dist')
        return self._f

    @property
    def flux(self):
        """The particle flux."""
        if self._flux is None:
            if self.hasflux:
                self._flux = self._create('flux')
        return self._flux

    def _create(
        self,
        name: str,
        unit: metric.UnitLike=None,
    ) -> physical.Array:
        """Create an array for the named quantity."""
        try:
            base = self.view.arrays[name]
        except KeyError as err:
            raise KeyError(f"No observable {name!r} in {self.view!r}") from err
        axes = {d: self.axes[d] for d in base.dimensions}
        array = physical.array(
            base.data,
            unit=metric.standardize(base.unit),
            axes=physical.axes(axes),
        )
        return array.withunit(unit or str(self.system))

    @property
    def hasdist(self):
        """True if this dataset contains the particle distribution.

        Datasets from EPREM runs with `streamFluxOutput=0`, which is the default
        setting, contain the full pitch-angle resolved particle distribution.
        This property allows users to check whether the underlying dataset
        contains the distribution (`True`) or not (`False`) before attempting to
        access the corresponding array property.

        See Also
        --------
        `~hasflux`
        """
        if self._hasdist is None:
            self._hasdist = 'Dist' in self.view.arrays
        return self._hasdist

    @property
    def hasflux(self):
        """True if this dataset contains the particle flux.

        Datasets from EPREM runs with `streamFluxOutput=1` contain pre-computed
        particle flux in place of the pitch-angle resolved particle
        distribution. This property allows users to check whether the underlying
        dataset contains pre-computed flux (`True`) or not (`False`) before
        attempting to access the corresponding array property.

        See Also
        --------
        `~hasdist`
        """
        if self._hasflux is None:
            self._hasflux = 'flux' in self.view.arrays
        return self._hasflux

    @property
    def view(self):
        """A view into this dataset on disk."""
        if self._view is None:
            self._view = view_factory(self.source)
        return self._view

    @property
    def axes(self):
        """An interface to canonical array axes."""
        if self._axes is None:
            self._axes = axes_factory(self.source, system=self.system)
        return self._axes

    @property
    def source(self):
        """This dataset's source path."""
        return self._source

    @property
    def system(self):
        """The metric system in which to represent this dataset."""
        return self._system


@etc.autostr
class Grid:
    """An interface to the coordinate arrays in a dataset.

    This is effectively a restricted version of `~Arrays` that serves as a
    convenient namespace for the coordinate-like quantities in a dataset.
    """

    def __init__(
        self,
        source: pathlib.Path,
        system: metric.System,
    ) -> None:
        """Initialize this interface."""
        self._arrays = arrays_factory(source, system)
        self._source = None
        self._system = None
        self._r = None
        self._theta = None
        self._phi = None

    @property
    def r(self):
        """The radial coordinate."""
        return self._arrays.r

    @property
    def theta(self):
        """The polar coordinate."""
        return self._arrays.theta

    @property
    def phi(self):
        """The azimuthal coordinate."""
        return self._arrays.phi

    @property
    def source(self):
        """The dataset's source path."""
        return self._arrays.source

    @property
    def system(self):
        """The dataset's metric system."""
        return self._arrays.system


def axes_factory(
    source: paths.PathLike,
    system: typing.Optional[typing.Union[str, metric.System]]=None,
) -> Axes:
    """Create an interface to all axes in a dataset."""
    return Axes(
        source=paths.fullpath(source, strict=True),
        system=metric.system(system or 'mks'),
    )


def arrays_factory(
    source: paths.PathLike,
    system: typing.Optional[typing.Union[str, metric.System]]=None,
) -> Arrays:
    """Create an interface to all arrays in a dataset."""
    return Arrays(
        source=paths.fullpath(source, strict=True),
        system=metric.system(system or 'mks'),
    )


def grid_factory(
    source: paths.PathLike,
    system: typing.Optional[typing.Union[str, metric.System]]=None,
) -> Grid:
    """Create an interface to the coordinate arrays in a dataset."""
    return Grid(source, system)


