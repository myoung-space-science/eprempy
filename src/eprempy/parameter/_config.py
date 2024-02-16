"""
Support for working with EPREM runtime configuration files.
"""

import collections.abc
import functools
import numbers
import pathlib
import re
import typing

from .. import etc
from .. import paths
from .. import symbolic
from . import _src


class Defaults(collections.abc.Mapping):
    """Default parameter values."""

    def __init__(self, srcdir: paths.PathLike) -> None:
        self._basetypes = _src.BaseTypesH(srcdir=srcdir)
        self._reference = _src.ConfigurationC(srcdir=srcdir)
        self._mapping = {
            key: _convert(parameter['defaultVal'], parameter['type'])
            for key, parameter in self.reference.items()
        }

    def __iter__(self) -> typing.Iterator[str]:
        """Called for iter(self)."""
        return iter(self.reference)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.reference)

    def __getitem__(self, name: str):
        """Retrieve a parameter value by name."""
        if name in self.reference:
            return self._evaluate(name)
        raise KeyError(f"Unknown parameter {name!r}")

    _special_cases = {
        'N_PROCS': None,
        'third': 1/3,
    }

    def _evaluate(self, current: typing.Union[str, numbers.Real]):
        """Compute the final value of a parameter."""
        if isinstance(current, numbers.Real):
            return current
        if value := cast(current, strict=False):
            return value
        if current in self._special_cases:
            return self._special_cases[current]
        argument = self._get_argument(current)
        if argument is not None:
            definition = argument['definition']
            if isinstance(definition, argument['type']):
                return definition
            return self._evaluate(definition)
        if isinstance(current, str):
            return self._resolve(current)
        raise TypeError(f"Can't evaluate {current!r}") from None

    _struct_member = re.compile(r'\Aconfig\.\w*\Z')

    def _resolve(self, definition: str):
        """Resolve a parameter definition into simpler components."""
        if self._struct_member.match(definition):
            return self._evaluate(definition.replace('config.', ''))
        interior = definition.strip('[]')
        if self._struct_member.match(interior):
            return [self._evaluate(interior.replace('config.', ''))]
        if result := self._compute_sum(definition):
            return result
        if any(c in definition for c in {'*', '/'}):
            expression = symbolic.expression(definition.replace('config.', ''))
            evaluated = [
                term.coefficient * self._evaluate(term.base)**term.exponent
                for term in expression
            ]
            return functools.reduce(lambda x,y: x*y, evaluated)
        raise TypeError(f"Can't resolve {definition!r}") from None

    def _compute_sum(self, arg: str) -> numbers.Real:
        """Compute the sum of two known parameters.
        
        Notes
        -----
        This is only designed to handle strings that contain a single additive
        operator joining two arguments that `_evaluate` already knows how to
        handle.
        """
        for operator in ('+', '-'):
            if operator in arg:
                terms = [
                    self._evaluate(s.strip())
                    for s in arg.split(operator)
                ]
                return terms[0] + float(f'{operator}1')*terms[1]

    def _get_argument(self, name: str):
        """Get the current definition and type of a parameter."""
        if name in self._mapping:
            return {
                'definition': self._mapping[name],
                'type': self.reference[name]['type']
            }
        if name in self.basetypes:
            return {
                'definition': self.basetypes[name],
                'type': type(self.basetypes[name]),
            }

    @property
    def reference(self):
        """Parameter metadata from `configuration.c`."""
        return self._reference

    @property
    def basetypes(self):
        """Values of constants defined in `baseTypes.h`."""
        return self._basetypes


def defaults_factory(srcdir: typing.Optional[paths.PathLike]=None):
    """Factory function for collections of default parameter values."""
    return Defaults(srcdir)


class ConfigKeyError(KeyError):
    pass


class ConfigDiff(typing.NamedTuple):
    """Return type of `ConfigFile.diff`."""

    keys: typing.Dict[int, set]
    full: typing.Dict[int, dict]


@etc.autostr
class ConfigFile(collections.abc.Mapping):
    """A class to handle EPREM run configuration files.

    Notes
    -----
    This interface was designed to provide a faithful representation of the
    information in a given configuration file. A few notable consequences are as
    follows:

    - The look-up methods do not accept aliases as keys.
    - The parsing routine does not attempt to cast parsed values from strings to
      their underlying types.
    - Values have no knowledge of their associated unit.

    See Also
    --------
    `~parameter.interface`
        Create an instance of `~parameter.Interface`, which supports aliased
        look-up, converts values to their underlying types, and returns a
        real-valued object with an associated unit when applicable.
    """
    def __init__(
        self,
        filepath: pathlib.Path,
        comments: typing.List[str],
    ) -> None:
        """Initialize this instance.

        This class is not intended for direct instantiation and initialization
        by general users. Instead, please see `~parameter.config`.
        """
        self._filepath = filepath
        self._comments = comments
        self._parsed = None

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return str(self.source)

    def __iter__(self) -> typing.Iterable[str]:
        """Called for iter(self)."""
        return iter(self.parsed)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.parsed)

    def __getitem__(self, key: str):
        """Get a value and unit for a configuration option."""
        if key in self.parsed:
            return self.parsed[key]
        raise ConfigKeyError(key)

    def compare(self, __o, **kwargs):
        """Compare this config file to another."""
        diff = self.diff(__o, **kwargs)
        df0 = diff.full[0]
        df1 = diff.full[1]
        keys = sorted(set(df0) | set(df1))
        return {k: (df0.get(k), df1.get(k)) for k in keys}

    def diff(self, __o, **kwargs):
        """Compute the symmetric difference between two config files."""
        def normalize(x):
            if isinstance(x, ConfigFile):
                return x
            if isinstance(x, (str, pathlib.Path)):
                return ConfigFile(x, **kwargs)
            raise TypeError(
                "Argument must be a path-like object"
                f" or an instance of this class (got {type(x)})"
            ) from None
        other = normalize(__o)
        keys = {
            0: set(self) - set(other),
            1: set(other) - set(self),
        }
        full = {
            0: dict(set(self.items())),
            1: dict(set(other.items())),
        }
        return ConfigDiff(keys=keys, full=full)

    @property
    def parsed(self):
        """The parsed parameter-value pairs."""
        if self._parsed is None:
            comments = set(self._comments or ['#'])
            self._parsed = _parse_config(self.source, comments)
        return self._parsed

    @property
    def source(self):
        """The path to the parsed configuration file."""
        return self._filepath


def _parse_config(
    filepath: pathlib.Path,
    comments: typing.Iterable[str]=None,
) -> typing.Dict[str, str]:
    """Parse an EPREM config file into a dictionary.

    This method opens the file that the given filepath points to and reads it
    line-by-line. It ignores lines that begin with a valid comment character and
    parses the rest into key-value pairs. It will automatically strip out inline
    comments.
    """
    pairs = {}
    cmnt = comments or ()
    with filepath.open('r') as fp:
        for line in fp:
            line = line.rstrip('\n')
            if line == '' or line == '\n' or line[0] in cmnt:
                continue
            tmp = paths.strip_inline_comments(line, cmnt)
            key, value = tmp.split('=')
            pairs[key.strip()] = value.strip()
    return pairs


def configfile_factory(
    filepath: paths.PathLike,
    comments: typing.Optional[typing.Iterable[str]]=None,
) -> ConfigFile:
    """Create an interface to an EPREM runtime configuration file.

    Parameters
    ----------
    filepath : string or path
        The path to the simulation configuration file to read. This function
        will convert the argument to a fully-qualified read-only path.

    comments : list of strings, default='#'
        List of single-character strings to interpret as comment markers in the
        configuration file. This function will automatically ignore lines that
        begin with either the empty string or the newline character.

    Returns
    -------
    `~ConfigFile`
        An interactive representation of the EPREM configuration file located at
        the given path.

    Notes
    -----
    - The argument to `filepath` may be relative but it must include the file
      name. For example, suppose the relevant configuration file is called
      `config.ini`. Then, passing `filepath='config.ini'` or
      `filepath='./config.ini'` within the containing directory, as well as
      `filepath='</path/to/dir>/config.ini'` elsewhere (even if `/path/to/dir`
      is relative), would be valid, but passing `filepath='</path/to/dir>'`
      (even if `/path/to/dir` is absolute) would not be valid.
    """
    return ConfigFile(
        paths.fullpath(filepath, strict=True),
        comments=list(comments or ['#']),
    )


_RT = typing.TypeVar('_RT')


def _convert(arg: typing.Union[str, _RT], realtype: _RT):
    """Convert `arg` to its real type, if necessary and possible."""
    if isinstance(arg, realtype):
        return arg
    if realtype in {int, float}:
        return soft_convert(arg, realtype)
    if realtype == list:
        return soft_convert(arg, stringlist)
    return arg


def soft_convert(
    string: str,
    convert: typing.Union[_RT, typing.Callable[[str], _RT]],
    acceptable: typing.Union[Exception, typing.Tuple[Exception]]=Exception,
) -> typing.Union[str, _RT]:
    """Convert a string to a different type, if possible.

    This function will use the given callable to attempt to convert the given
    string to a different type. If the conversion fails, this function will
    return the unconverted string.

    Parameters
    ----------
    string
        The string to convert.

    convert : callable
        A callable object that accepts a string argument and returns the
        converted value.

    acceptable : exception or iterable of exceptions
        One or more types of valid exception classes that this function should
        ignore when attempting to convert `string`. The default behavior is to
        accept any subclass of `Exception`. Passing arguments to this keyword
        therefore allows the caller to limit the scope of ignorable errors.

    Returns
    -------
    converted type or string
        The converted value of the given string, if conversion succeeded, or the
        unconverted string.
    """
    try:
        value = convert(string)
    except acceptable or Exception:
        return string
    return value


def stringlist(string: str) -> list:
    """Convert a string representation of a list to a list"""
    if not (string.startswith('[') and string.endswith(']')):
        raise TypeError(f"Can't convert {string!r} to a list") from None
    inside = string.strip('[]')
    if not inside:
        return []
    items = [item.strip(" ''") for item in inside.split(',')]
    return [cast(i) for i in items]


_NT = typing.TypeVar('_NT', bound=numbers.Number)


def cast(
    arg: _NT,
    strict: bool=True,
) -> typing.Union[int, float, complex, _NT]:
    """Attempt to convert `arg` to an appropriate numeric type.
    
    Parameters
    ----------
    arg
        The object to convert. May be of any type. If it has a numeric type,
        this function will immediately return it.

    strict : bool, default=True
        If true (default), this function will raise an exception if it can't
        convert `arg` to a numerical type. If false, this function will silently
        return upon failure to convert.

    Returns
    -------
    number
        The numerical value of `arg`, if possible. See description of `strict`
        for behavior after failed conversion.
    """
    if isinstance(arg, numbers.Number):
        return arg
    types = (
        int,
        float,
        complex,
    )
    for t in types:
        try:
            return t(arg)
        except ValueError:
            pass
    if strict:
        raise TypeError(f"Can't convert {arg!r} to a number") from None


