import collections.abc
import contextlib
import pathlib
import typing

from .. import dataset
from .. import etc
from .. import metric
from .. import observable
from .. import parameter
from .. import paths
from .. import reference


class Paths(typing.NamedTuple):
    """Fully-qualified paths relevant to a given observer."""
    source: pathlib.Path
    """The full path to an observer's data."""
    config: pathlib.Path
    """The full path to an observer's configuration file."""


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
        __id: typing.Union[str, int],
        paths: Paths,
        system: metric.System,
    ) -> None:
        self._id = __id
        self._paths = paths
        self._system = system
        self._parameters = None
        self._observables = None
        self._source = None
        self._dataset = None
        self._config = None
        self._sizes = None

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return repr(self._id)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.observables) + len(self.parameters)

    def __iter__(self):
        """Called for iter(self)."""
        return iter(tuple(self.observables) + tuple(self.parameters))

    def __getitem__(self, key: str, /):
        """Retrieve the named quantity, if possible."""
        if key in self.observables:
            return self.observables[key]
        if key in self.parameters:
            return self.parameters[key]
        raise KeyError(
            f"No observable quantity or parameter value for {key!r}"
        ) from None

    def which(
        self,
        category: typing.Union[
            typing.Literal['observables'],
            typing.Literal['parameters'],
        ],
    ) -> None:
        """Print names of available quantities."""
        if category == 'observables':
            for group in reference.OBSERVABLES.aliases:
                print(' == '.join(repr(i) for i in group))
        elif category == 'parameters':
            for group in self.parameters.keys(aliased=True):
                print(' == '.join(repr(i) for i in group))
        else:
            raise ValueError(
                f"Unknown category of quantities: {category!r}"
            ) from None

    @property
    def observables(self):
        """An interface to observable array-like quantities."""
        if self._observables is None:
            self._observables = observable.quantities(
                self._paths.source,
                self._paths.config,
                self.system,
            )
        return self._observables

    @property
    def source(self):
        """The directory containing this observer's dataset."""
        if self._source is None:
            self._source = self.dataset.source.parent
        return self._source

    @property
    def dataset(self):
        """An interface to this observer's raw dataset."""
        if self._dataset is None:
            self._dataset = dataset.view(self._paths.source)
        return self._dataset

    @property
    def parameters(self):
        """An interface to simulation parameter values."""
        if self._parameters is None:
            self._parameters = parameter.interface(self._paths.config)
        return self._parameters

    @property
    def config(self):
        """An interface to this observer's raw configuration file."""
        if self._config is None:
            self._config = parameter.configfile(self._paths.config)
        return self._config

    @property
    def system(self):
        """This observer's metric system."""
        return self._system


def factory(
    __id: typing.Union[str, int],
    config: paths.PathLike=None,
    source: paths.PathLike=None,
    system: str=None,
) -> Observer:
    """Create a general EPREM observer interface."""
    p = _build_paths(__id, source=source, config=config)
    system = metric.system(system or 'mks')
    return Observer(__id, p, system=system)


def _build_paths(
    idtag,
    /,
    source: paths.PathLike=None,
    config: paths.PathLike=None,
) -> Paths:
    """Initialize observer paths from arguments."""
    errmsg = f"Cannot create path to observer data from {source!r}"
    directory = paths.fullpath(source or '.', strict=True)
    if not directory.is_dir():
        raise ValueError(errmsg) from None
    confpath = _build_config_path(directory, config)
    datapath = None
    if isinstance(idtag, int):
        for prefix in {'obs', 'flux'}:
            path = directory / f'{prefix}{idtag:06}.nc'
            with contextlib.suppress(paths.NonExistentPathError):
                datapath = paths.fullpath(path, strict=True)
        if datapath is None:
            raise ValueError(errmsg)
        return Paths(source=datapath, config=confpath)
    if isinstance(idtag, str):
        for name in {f'p_obs{int(idtag):03}', idtag}:
            path = directory / f'{name}.nc'
            with contextlib.suppress(paths.NonExistentPathError):
                datapath = paths.fullpath(path, strict=True)
        if datapath is None:
            raise ValueError(errmsg)
        return Paths(source=datapath, config=confpath)
    raise ValueError(
        f"Cannot initialize observer paths from {source!r} and {config!r}"
    ) from None


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


