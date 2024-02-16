"""
Support for working with EPREM source files.
"""

import abc
import collections.abc
import json
import numbers
import pathlib
import re
import typing

from .. import container
from .. import paths
from .. import symbolic
from . import _metadata


class SourceFile(collections.abc.Mapping):
    """An object representing parameters in an EPREM source file."""

    _db_path = pathlib.Path(__file__).parent / 'reference.json'

    def __init__(
        self,
        db_key: str,
        filename: str,
        srcdir: typing.Union[str, pathlib.Path]=None,
    ) -> None:
        """Initialize an instance of this class."""
        path = self.build_path(filename, srcdir)
        if path and path.exists():
            loaded = self.load_from_source(paths.TextFile(path))
            self._origin = path
        else:
            loaded = self.load_from_package(db_key)
            self._origin = self._db_path
        self._definitions = self.standardize(loaded)

    @property
    def origin(self):
        """The path to definitions.
        
        This property represents the user-provided path to the source code used
        to build the instance definitions, or the path to the database of
        default definitions.
        """
        return self._origin

    def __iter__(self) -> typing.Iterator:
        """Called for iter(self)."""
        return iter(self.definitions)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.definitions)

    @property
    def definitions(self):
        """The parameter definitions in this file."""
        return self._definitions

    @abc.abstractmethod
    def standardize(self, loaded: dict):
        """Convert loaded attributes into standard definitions.
        
        This abstract method provides a default implementation that simply
        returns the input object.
        """
        return loaded

    def build_path(
        self,
        filename: str,
        source: paths.PathLike=None,
    ) -> typing.Optional[pathlib.Path]:
        """Create the full path to the source file, if possible."""
        try:
            path = paths.fullpath(source, strict=True)
            if path.is_dir():
                path /= filename
        except TypeError:
            path = None
        return path

    def load_from_package(self, key: str) -> dict:
        """Load argument definitions from the package defaults."""
        with self._db_path.open('r') as fp:
            loaded = json.load(fp)
        return loaded[key]

    @abc.abstractmethod
    def load_from_source(self, file: paths.TextFile) -> dict:
        """Load argument definitions from the source file."""
        pass

    def get(self, key: str, default: typing.Any=None, format: str=None):
        """Get (and optionally format) a parameter value or `default`.
        
        The default implementation is identical to `collections.abc.Mapping.get`
        when `format=None`, and otherwise raises an exception. Concrete
        subclasses may wish to define additional `format`-based behavior by
        overloading this method.
        """
        if not format:
            return super().get(key, default)
        raise NotImplementedError(f"Unrecognized format {format}")

    def todict(self, mode: str=None, sort: bool=False):
        """Convert this object to a `dict` according to `mode`.
        
        Parameters
        ----------
        mode : string, optional
            A defined formatting mode. This method will pass `mode` to the
            `format` keyword of `~get` for each value.

        sort : boolean, default=false
            If true, sort the parameters before creating the `dict`. The default
            behavior is to respect insertion order.
        """
        keys = sorted(self.keys()) if sort else self.keys()
        return {key: self.get(key, format=mode) for key in keys}

    def tolines(self, indent: int=0, **kwargs):
        """Convert this object to a `list` of `str`.

        Parameters
        ----------
        indent : int, default=0
            The number of spaces to indent each line.

        **kwargs
            Additional options to pass to `~todict`.
        """
        lines = []
        pad = indent * ' '
        selfdict = self.todict(**kwargs)
        for name, current in selfdict.items():
            if isinstance(current, typing.Mapping):
                value = '\n'.join(
                    f"{pad}{pad}{k!r}: {v if k == 'type' else repr(v)},"
                    for k, v in current.items()
                )
            else:
                value = current
            line = f"{pad}{name!r}" + ": {\n" + f"{value}\n{pad}" + "}"
            lines.append(line)
        return lines

    def tostring(self, **kwargs):
        """Convert this object to a formatted string.
        
        This method will pass all arguments to `~tolines`. The default
        implementation simply joins the result of `~tolines` via `str.join`.
        """
        lines = self.tolines(**kwargs)
        return '\n'.join(f"{line}," for line in lines)


class BaseTypeDef:
    """Pattern parser for defined constants in baseTypes.h."""

    @property
    def pattern(self):
        return re.compile(r"""
            # the start of the string (no following whitespace)
            \A
            # the `#define` pre-processor directive
            \#define
            # at least one whitespace character
            \s+
            # the defined name
            (?P<name>[0-9A-Z_]+)
            # at least one whitespace character
            \s+
            # the defined value
            (?P<value>[-+\.\*\/\d\w\s\(\)]+)
            # the end of the string (no trailing whitespace)
            \Z
        """, re.VERBOSE)

    def match(self, line: str):
        """Identify lines that define a runtime constant."""
        if match := self.pattern.match(line.strip()):
            return match.groupdict()

    def parse(self, parsable: typing.Dict[str, str]):
        """Parse a line that defines a runtime constant."""
        return parsable['name'], parsable['value']


class BaseTypesH(SourceFile):
    """A representation of constant values in EPREM `baseTypes.h`."""

    def __init__(self, srcdir: typing.Union[str, pathlib.Path]=None) -> None:
        super().__init__('BASETYPES_H', 'baseTypes.h', srcdir)
        self._types = None
        self._cache = {}

    def standardize(self, loaded: dict):
        return super().standardize(loaded)

    def load_from_source(self, file: paths.TextFile) -> dict:
        typedef = BaseTypeDef()
        return file.extract(typedef.match, typedef.parse)

    def get(self, key: str, default: typing.Any=None, format: str=None):
        if format == 'raw':
            value = self.definitions.get(key, default)
            if isinstance(value, symbolic.Expression):
                return value.format(separator=' * ')
            return value
        if format == 'full':
            value = self.get(key, default)
            result = {'value': value}
            for k, v in _metadata._BASETYPES_H.get(key, {}).items():
                result[k] = v.__name__ if k == 'type' else v
            return result
        return super().get(key, default, format)

    def tostring(self, **kwargs):
        s = super().tostring(**kwargs)
        return 'BASETYPES_H = {\n' + f"{s}" + '\n}'

    def __getitem__(self, key: str) -> numbers.Real:
        """Access constants by keyword."""
        if key in self._cache:
            return self._cache[key]
        if key in self.definitions:
            value = self._compute(key)
            self._cache[key] = value
            return value
        raise KeyError(f"No {key!r} in {self!r}")

    def _compute(self, key: str) -> numbers.Real:
        """Compute the value of a defined constant."""
        target = self.definitions[key]
        realtype = self.types.get(key)
        if isinstance(target, realtype):
            return target
        if any(c in target for c in {'*', '/', 'sqrt'}):
            return self._evaluate(symbolic.expression(target))
        if realtype:
            return realtype(target)
        raise TypeError(target)

    @property
    def types(self):
        """The type of each constant."""
        if self._types is None:
            self._types = {
                k: v['type'] for k, v in _metadata._BASETYPES_H.items()
            }
        return self._types

    def _evaluate(self, expression: symbolic.Expression):
        """Internal method for evaluating symbolic definitions."""
        value = 1.0
        for term in expression:
            if term.base in self.definitions:
                value *= float(term(self._compute(term.base)))
            elif term.base == '1':
                value *= float(term)
        return value


class FunctionCall:
    """Pattern parser for function calls."""

    # TODO: 
    # - __init__ should take arguments that allow the user to define possible
    #   function names (e.g., 'readInt', 'readDouble') and target-variable
    #   prefix (e.g., 'config').
    # - It may be better to just grab everything in parentheses as `args` and
    #   let `parse` sort them out.

    @property
    def pattern(self):
        return re.compile(r"""
            # the start of the string, followed by optional whitespace
            \A\s*
            # the assignment target (possibly a struct member)
            (?:config\.)?\w+
            # equals sign surrounded by optional whitespace
            \s*=\s*
            # kludge for `(char*)readString(...)`
            (?:\(char\*\))?
            # the name of the file-reading method
            (?P<mode>read(?:Int|Double|DoubleArray|String))
            # beginning of function call
            \(
                # the parameter key in the config file
                (?P<key>\"\w*\")
                # optional whitespace followed by a comma
                \s*\,
                # the remaining arguments
                (?P<args>.*?)
            # end of function call
            \)
            # C statement terminator
            \;
            # optional whitespace, followed by the end of the string
            \s*\Z
        """, re.VERBOSE)

    def match(self, line: str):
        """Identify lines that read config-file input."""
        if match := self.pattern.match(line.strip()):
            return match.groupdict()

    def parse(self, parsable: typing.Dict[str, str]):
        """Parse a line that reads config-file input."""
        parsed = {}
        key = parsable['key'].strip(' "')
        mode = parsable['mode']
        args = parsable['args'].split(',')
        parsed.update(self._normalize(mode, args))
        return key, parsed

    _keys = {
        'readInt': ['defaultVal', 'minVal', 'maxVal'],
        'readDouble': ['defaultVal', 'minVal', 'maxVal'],
        'readString': ['defaultVal'],
        'readDoubleArray': [
            'defaultSize',
            'size',
            'defaultVal',
            'minVal',
            'maxVal',
        ],
    }

    def _normalize(self, mode: str, args: typing.Iterable[str]):
        """Determine argument type and keys from `mode`."""
        pairs = dict(zip(self._keys[mode], [arg.strip(' "') for arg in args]))
        return {'mode': mode, **pairs}


class VariableDefinition:
    """Pattern parser for variable definitions."""

    # TODO:
    # - __init__ should take arguments that allow the user to define the
    #   variable type (e.g., 'Scalar_t').
    # - Can the pattern identify things like `size` and `value` with optional
    #   user input, or does `parse` need to handle that?

    @property
    def pattern(self):
        return re.compile(r"""
            # the start of the string, followed by optional whitespace
            \A\s*
            # type declaration
            Scalar\_t
            # optional whitespace
            \s*
            # variable name
            (?P<name>\w+)
            # array size
            \[(?P<size>\d+)\]
            # equals sign surrounded by optional whitespace
            \s*=\s*
            # array value(s)
            \{(?P<value>(\d*(?:\.\d+)?)|((?:config\.)?\w+))\}
            # C statement terminator
            \;
            # optional whitespace, followed by the end of the string
            \s*\Z
        """, re.VERBOSE)

    def match(self, line: str):
        """Identify lines that define a variable."""
        if match := self.pattern.match(line.strip()):
            return match.groupdict()

    def parse(self, parsable: typing.Dict[str, str]):
        """Parse information about a defined variable."""
        parsed = {
            'size': int(parsable['size']),
            'value': f"[{','.join(container.wrap(parsable['value']))}]",
        }
        return parsable['name'], parsed


class ConfigurationC(SourceFile):
    """A representation of default arguments in EPREM `configuration.c`."""

    _types = container.Bijection(
        {
            'readInt': int,
            'readDouble': float,
            'readString': str,
            'readDoubleArray': list,
        }
    )

    def __init__(self, srcdir: typing.Union[str, pathlib.Path]=None) -> None:
        super().__init__('CONFIGURATION_C', 'configuration.c', srcdir)

    def standardize(self, loaded: dict):
        return self._replace(loaded, 'mode', 'type', self._types)

    def load_from_source(self, file: paths.TextFile) -> dict:
        assignments = self._get_assignments(file)
        arrays = self._get_array_defaults(file)
        subs = {
            key: {
                'mode': assigned['mode'],
                'defaultVal': arrays[assigned['defaultVal']]['value'],
                'maxVal': assigned['maxVal'],
                'minVal': assigned['minVal'],
            } for key, assigned in assignments.items()
            if assigned['defaultVal'] in arrays
        }
        return {
            key: subs.get(key, attrs)
            for key, attrs in assignments.items()
        }

    def __getitem__(self, key: str) -> typing.Dict[str, typing.Any]:
        """Request a reference object by parameter name."""
        if key in self.definitions:
            return self.definitions[key]
        raise KeyError(f"No reference information for {key!r}")

    def get(self, key: str, default: typing.Any=None, format: str=None):
        if format == 'raw':
            modes = self._types.invert()
            loaded = self._replace(self.definitions, 'type', 'mode', modes)
            return loaded.get(key, default)
        if format == 'full':
            defined = self.definitions.get(key, default)
            loaded = {**defined, **_metadata._CONFIGURATION_C.get(key, {})}
            return {
                k: v.__name__ if k == 'type' else v
                for k, v in loaded.items()
            }
        return super().get(key, default, format)

    def tostring(self, **kwargs):
        s = super().tostring(**kwargs)
        return 'CONFIGURATION_C = {\n' + f"{s}" + '\n}'

    def _get_assignments(self, file: paths.TextFile):
        """Get the assigned default values from function calls."""
        pattern = FunctionCall()
        return file.extract(pattern.match, pattern.parse)

    def _get_array_defaults(self, file: paths.TextFile):
        """Get all array default values defined in the source."""
        pattern = VariableDefinition()
        return file.extract(pattern.match, pattern.parse)

    def _replace(
        self,
        mapping: typing.Mapping[str, typing.Mapping],
        old: str,
        new: str,
        conversion: typing.Mapping,
    ) -> typing.Mapping[str, typing.Mapping]:
        """Convert values in the interior mappings of `mapping`."""
        return {
            key: {
                new: conversion[interior[old]],
                **{k: v for k, v in interior.items() if k != old}
            } for key, interior in mapping.items()
        }


