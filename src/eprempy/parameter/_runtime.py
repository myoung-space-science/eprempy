"""
Interfaces to runtime parameter values.
"""

import pathlib
import typing

import numpy

from .. import aliased
from .. import container
from .. import measured
from .. import metric
from .. import numeric
from .. import paths
from .. import physical
from .. import real
from . import _config
from . import _metadata


T = typing.TypeVar('T')


class Variable(physical.Vector[real.ValueType]):
    """A vector-like object with conditional cast to built-in type.

    An instance of this class is a physical vector that also supports converting
    single-valued instances to built-in `int`, `float`, or `complex` type.
    """

    def __getitem__(self, *args):
        """Extract a sub-collection.
        
        Notes
        -----
        - This method is designed to return a `~Scalar` when the given arguments
          produce 0-D data.
        """
        idx = container.unwrap(args)
        if isinstance(idx, typing.SupportsIndex) and idx < 0:
            idx += len(self)
        data = self.data[idx]
        if container.length(data) == 0:
            return physical.scalar(data, unit=self.unit)
        return variable_factory(data, unit=self.unit)

    def __int__(self):
        return self._as_builtin(int)

    def __float__(self):
        return self._as_builtin(float)

    def __complex__(self):
        return complex(float(self))

    def __round__(self, ndigits=None):
        """Called for round(self)."""
        return self._as_scalar(numeric.operators.round, ndigits=ndigits)

    def __floor__(self):
        """Called for math.floor(self)."""
        return self._as_scalar(numeric.operators.floor)

    def __ceil__(self):
        """Called for math.ceil(self)."""
        return self._as_scalar(numeric.operators.ceil)

    def __trunc__(self):
        """Called for math.trunc(self)."""
        return self._as_scalar(numeric.operators.trunc)

    def _as_scalar(self, f: typing.Callable, **kwargs):
        """Return the result of `f` as a `~Scalar`."""
        try:
            data = f(self.data[0], **kwargs)
        except TypeError as err:
            raise TypeError(
                f"Cannot apply {f.__name__} to size-{self.size} variable"
            ) from err
        return physical.scalar(data, self.unit)

    def _as_builtin(self, t: T):
        """Convert this instance to a built-in numeric type."""
        try:
            result = t(self.data[0])
        except TypeError as err:
            raise TypeError(
                f"Cannot convert a size-{self.size} variable to {t!r}"
            ) from err
        return result

    def _singular(self):
        """Represent this object as a single value only if possible."""
        size = self.size
        if size == 1:
            return self.data[0]
        raise TypeError(
            f"Cannot represent a size-{size} variable as a number"
        ) from None


@Variable.register.factory
def variable_factory(x, /, unit=None) -> Variable:
    """Factory function for `~Variable`."""
    d, u = variable_args(x, unit)
    ctx = measured.context(u, measured.convert.arraylike)
    return Variable(d, ctx)


def variable_args(x, unit, /):
    """Parse arguments to initialize `~Variable`.

    Notes
    -----
    - If `x` is an instance of `~Variable`, this function will return copies of
      the data and unit. Otherwise, it will attempt to construct an instance of
      `~physical.Vector` from the data and unit, then return a copy of that
      vector's data and unit.
    """
    if isinstance(x, measured.Object):
        vector = physical.vector(x)
        return vector.data, vector.unit
    try:
        vector = physical.vector(numpy.array(x, ndmin=1), unit=unit)
    except (TypeError, ValueError) as err:
        lowercase = ('vector', 'variable')
        capitalized = ('Vector', 'Variable')
        m = str(err).replace(*lowercase).replace(*capitalized)
        raise type(err)(m)
    return vector.data, vector.unit


_VT = typing.TypeVar('_VT')


class Interface(aliased.Mapping[str, _VT]):
    """An interface to EPREM parameter values."""

    def __init__(
        self,
        base: typing.Mapping[str, typing.Any],
        defaults: _config.Defaults,
        cfgpath: typing.Optional[pathlib.Path],
    ) -> None:
        """Interface initializer.

        Not meant for public use. Please see `~interface`.
        """
        super().__init__(base, aliases=_metadata.ALIASES)
        self._defaults = defaults
        self._config = cfgpath

    def __repr__(self) -> str:
        clsname = self.__class__.__qualname__
        if self.config is None:
            return f"{clsname}(source={str(self.source)!r})"
        display = {
            'config': str(self.config),
            'source': str(self.source),
        }
        args = ', '.join(f"{k}={v!r}" for k, v in display.items())
        return f"{clsname}({args})"

    def __getitem__(self, __k: str):
        """Create the appropriate object for the named parameter."""
        try:
            this = super().__getitem__(__k)
        except KeyError:
            raise KeyError(f"No parameter corresponding to {__k!r}") from None
        value = this['value']
        unit = this['unit']
        usedeg = super().__getitem__('useDegrees')
        if unit == 'rad' and usedeg['value']:
            unit = 'deg'
        if unit is None:
            return value
        return variable_factory(value, unit=unit)

    @property
    def source(self):
        """The source of default values.
        
        If this interface was initialized with a path to an EPREM `src`
        directory, the value of this property will be that path. Otherwise, it
        will be the path to the database of default values.
        """
        return self.reference.origin

    @property
    def basetypes(self):
        """Values of constants defined in `baseTypes.h`."""
        return self._defaults.basetypes

    @property
    def reference(self):
        """Metadata and default values from from `configuration.c`."""
        return self._defaults.reference

    @property
    def config(self):
        """The full path to the relevant configuration file, if given."""
        return self._config


def interface_factory(*args, **kwargs):
    cfginit, srcinit, options = _init_interface(args, kwargs)
    defaults = _config.Defaults(srcdir=srcinit)
    local = {
        key: info.get('default')
        for key, info in _metadata._LOCAL.items()
    }
    init = {**local, **defaults}
    cfgpath = None
    if cfginit:
        cfgfile = _config.configfile_factory(cfginit, **options)
        cfgpath = cfgfile.source
        user = {
            # NOTE: this does not use `configfile.get(key)` because we don't
            # want to overwrite the default value with `None` if the config
            # file doesn't include a given parameter.
            key: _config._convert(cfgfile[key], parameter['type'])
            for key, parameter in defaults.reference.items()
            if key in cfgfile
        }
        init.update(user)
    base = {
        key: {'unit': _metadata.UNITS.get(key), 'value': value}
        for key, value in init.items()
    }
    return Interface(base, defaults, cfgpath)


def _init_interface(
    args: typing.Tuple[paths.PathLike, paths.PathLike],
    kwargs: dict,
) -> typing.Tuple[paths.PathLike, paths.PathLike, dict]:
    """Internal initialization parser for `~interface` function."""
    if len(args) == 2:
        return *args, kwargs
    if len(args) == 1:
        source = kwargs.pop('srcdir', None)
        return args[0], source, kwargs
    if len(args) == 0:
        config = kwargs.pop('config', None)
        source = kwargs.pop('srcdir', None)
        return config, source, kwargs
    raise TypeError(args, kwargs)


