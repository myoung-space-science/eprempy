"""
EPREM observer interfaces.
"""

import collections.abc
import pathlib

from . import datafile
from . import etc
from . import metric
from . import observable
from . import parameter
from . import paths
from .observer import (
    Stream,
    Point,
    stream_factory as stream,
    point_factory as point,
)


__all__ = [
    "Stream",
    "Point",
    "stream",
    "point",
    "observer",
    "Observer",
]


@etc.autostr
class Observer(collections.abc.Mapping):
    """A generic EPREM observer.

    An instance of this class provides interfaces to observable array-like
    quantities via its `observables` property, and to simulation parameter
    values via its `parameters` property. It also implements a mapping-style
    interface to all observable quantities and simulation parameters as a flat
    collection.
    """

    def __init__(
        self,
        dataview: datafile.View,
        observables: observable.Quantities,
    ) -> None:
        self._dataview = dataview
        self._observables = observables
        self._source = None
        self._system = None
        self._sizes = None
        self._axes = None
        self._times = None
        self._shells = None
        self._species = None
        self._energies = None
        self._mus = None

    def __hash__(self):
        """Called for hash(self)."""
        return hash(self.source)

    def __str__(self) -> str:
        """An unambiguous representation of this object."""
        return str(self.source)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.observables)

    def __iter__(self):
        """Called for iter(self)."""
        return iter(tuple(self.observables))

    def __getitem__(self, key: str, /):
        """Retrieve the named quantity, if possible."""
        if key in self._observables:
            return self._observables[key]
        raise KeyError(
            f"No observable quantity for {key!r}"
        ) from None

    @property
    def times(self):
        """This observer's time coordinates."""
        if self._times is None:
            self._times = self._get_axis('time')
        return self._times

    @property
    def shells(self):
        """This observer's shell numbers."""
        if self._shells is None:
            self._shells = self._get_axis('shell')
        return self._shells

    @property
    def species(self):
        """This observer's species symbols."""
        if self._species is None:
            self._species = self._get_axis('species')
        return self._species

    @property
    def energies(self):
        """This observer's energy coordinates."""
        if self._energies is None:
            self._energies = self._get_axis('energy')
        return self._energies

    @property
    def mus(self):
        """This observer's mu coordinates."""
        if self._mus is None:
            self._mus = self._get_axis('mu')
        return self._mus

    def _get_axis(self, name: str):
        """Internal helper for axis properties."""
        if self._axes is None:
            self._axes = datafile.axes(self.source, self.system)
        return self._axes[name]

    @property
    def source(self):
        """The directory containing this observer's dataset."""
        if self._source is None:
            self._source = self.dataview.source
        return self._source

    @property
    def system(self):
        """This observer's metric system."""
        if self._system is None:
            self._system = self.observables.system
        return self._system

    @property
    def observables(self):
        """An interface to observable array-like quantities."""
        return self._observables

    @property
    def dataview(self):
        """An interface to this observer's raw dataset."""
        return self._dataview


class Dataset:
    """An interface to a complete EPREM dataset."""

    def __init__(
        self,
        directory: pathlib.Path,
        parameters: parameter.Interface,
        config: parameter.ConfigFile,
        system: metric.System,
    ) -> None:
        self._directory = directory
        self._parameters = parameters
        self._config = config
        self._system = system
        self._observers = None

    @property
    def observers(self):
        """A mapping of available observer files."""
        if self._observers is None:
            prefixes = ('obs', 'flux', 'p_obs')
            obspaths = [
                path
                for prefix in prefixes
                for path in self.directory.glob(f"{prefix}*")
            ]
            self._observers = {
                _get_observer_id(path): self._new_observer(path)
                for path in obspaths
            }
        return self._observers

    def _new_observer(self, path: pathlib.Path):
        """Create a new general observer interface."""
        dataview = datafile.view(source=path)
        observables = observable.quantities(
            source=self.directory,
            config=self.config.source,
            system=self.system,
        )
        return Observer(dataview, observables)

    @property
    def directory(self):
        """The full path to EPREM output files."""
        return self._directory

    @property
    def parameters(self):
        """An interface to simulation parameter values."""
        return self._parameters

    @property
    def config(self):
        """An interface to this observer's raw configuration file."""
        return self._config

    @property
    def system(self):
        """This observer's metric system."""
        return self._system


def _get_observer_id(path: pathlib.Path):
    """Compute the appropriate observer ID for the given path."""
    stem = path.stem
    for prefix in ('obs', 'flux', 'p_obs'):
        if stem.startswith(prefix):
            key = stem.lstrip(prefix)
            if prefix in {'obs', 'flux'}:
                return int(key)
            return key
    raise ValueError(path)


def dataset(
    source: paths.PathLike=None,
    config: paths.PathLike=None,
    system: str=None,
) -> Dataset:
    """Create an EPREM dataset interface."""
    directory = paths.fullpath(source, strict=True)
    confpath = _build_config_path(directory, config=config)
    return Dataset(
        directory,
        config=parameter.configfile(confpath),
        parameters=parameter.interface(confpath),
        system=metric.system(system or 'mks'),
    )


_CONFIG_NAMES = (
    'eprem_input_file',
    '*.cfg',
    '*.ini',
    '*.in',
)

def _build_config_path(
    directory: pathlib.Path,
    config: paths.PathLike=None,
) -> pathlib.Path:
    """Create the full path to the requested config file, if possible."""
    if config is None: # need to guess
        for name in _CONFIG_NAMES:
            if found := next(directory.glob(name), None):
                return found
        raise ValueError(
            f"Cannot guess name of config file in {directory}"
        ) from None
    this = pathlib.Path(config)
    full = (
        directory / config if this.name == config # file name only
        else paths.fullpath(this, strict=True) # full or relative path
    )
    if full.exists():
        return full
    raise ValueError(
        f"Cannot determine path to config file from {config!r}"
    ) from None


