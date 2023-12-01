"""
Support for the EPREM parameters command-line utility.
"""

import datetime
import json
import os
import pathlib
import typing

from eprempy import etc
from eprempy import measured
from eprempy import parameter
from eprempy.parameter._src import (
    BaseTypesH,
    ConfigurationC,
    SourceFile,
)
from eprempy import paths
from eprempy.exceptions import (
    UserError,
    CLIError,
)


DIRECTORY = pathlib.Path(__file__).expanduser().resolve().parent
"""The fully resolved directory containing this file."""


def compare_arguments(
    files: typing.Iterable[paths.PathLike],
    source: paths.PathLike=None,
    diff: bool=False,
    names: bool=False,
) -> None:
    """Compare values of EPREM configuration parameters.
    
    This method will print the name of each parameter and its default value, as
    well as the corresponding value contained in each configuration file in
    `paths`. If `source` is not absent, it will read parameter names and default
    values from the version of `configuration.c` in `source`; otherwise it will
    use the values in the local database.
    """
    if not files:
        raise UserError("Nothing to compare") from None
    args = _build_arg_dict(files, source=source, diff=diff, names=names)
    topkeys = next(list(v.keys()) for v in args.values() if v)
    nonnull = (v for item in args.values() for v in item.values() if v)
    # width (i.e., string length) of the longest parameter
    pwidth = max(len(k) for k in args)
    # width (i.e., string length) of the longest file key
    lwidth = max(len(k) for k in topkeys)
    # width (i.e., string length) of the longest non-null value
    vwidth = max(len(v) for v in nonnull)
    # padded parameter-value width
    rwidth = vwidth + 2
    # amount of parameter-value right-justification
    jwidth = min(78, rwidth)
    # total width: either the longest parameter or the longest key-value combo.
    # - longest parameter produces groups like
    # * ParameterName
    # * -------------
    # * key     value
    # - longest key-value combo produces groups like
    # *    ParameterName
    # * -------------------
    # * key           value
    cwidth = max(pwidth, lwidth + jwidth)
    print()
    for key, item in args.items():
        print(str(key).center(cwidth))
        print('-' * cwidth)
        for k, v in item.items():
            print(f"{str(k).ljust(lwidth)}{str(v).rjust(jwidth)}")
        print()


def _build_arg_dict(
    files: typing.Iterable[paths.PathLike],
    source: paths.PathLike=None,
    diff: bool=False,
    names: bool=False,
) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
    """Build a `dict` of parameter values."""
    default = parameter.interface()
    normalized = _normalize_paths(files)
    if names:
        mapped = normalized
    else:
        mapped = {k: str(i) for i, k in enumerate(normalized)}
    targets = {
        relpath: parameter.interface(abspath)
        for abspath, relpath in mapped.items()
    }
    keys = sorted(ConfigurationC(source))
    built = {key: {} for key in keys}
    for key in keys:
        current = {
            name: _format_arg(interface.get(key))
            for name, interface in targets.items()
        }
        values = list(current.values())
        v0 = values[0]
        if not diff or any(vi != v0 for vi in values):
            built[key] = {
                'default': _format_arg(default[key]),
                **current,
            }
    if diff:
        return {k: v for k, v in built.items() if v}
    return built


def _normalize_paths(args: typing.Iterable[paths.PathLike]):
    """Compute full and unique relative paths."""
    full = {
        str(arg): str(paths.fullpath(arg, strict=True))
        for arg in args
    }
    common = os.path.commonpath(full.values())
    return {
        str(path): os.path.relpath(path, start=common)
        for path in full.values()
    }


def _format_arg(arg):
    """Format this argument for display."""
    if isinstance(arg, measured.Object):
        data = arg.data[0] if len(arg.data) == 1 else arg.data
        if arg.unit == '1' or data is None:
            return f"{data!r}"
        if str(arg.unit) in {'d', 'day'}:
            return f"{data} 'day'"
        return f"{data} {str(arg.unit)!r}"
    return str(arg)


_DB_PATH = SourceFile._db_path

_PY_PATH = _DB_PATH.parent / 'default.py'

DB_PATH = str(_DB_PATH)
"""Public string version of source file default database path."""


def generate_defaults(
    source: paths.PathLike,
    append: bool=False,
    verbose: bool=False,
) -> None:
    """Generate default arguments from the EPREM source code in `src`."""
    basetypes_h = BaseTypesH(source)
    configuration_c = ConfigurationC(source)
    action = 'Appended' if append else 'Wrote'
    _generate_json(basetypes_h, configuration_c, _DB_PATH, append=append)
    if verbose:
        print(f"{action} new database to {_DB_PATH}")
    _generate_py(basetypes_h, configuration_c, _PY_PATH)
    if verbose:
        print(f"{action} new variables to {_PY_PATH}")


def _generate_json(
    basetypes_h: BaseTypesH,
    configuration_c: ConfigurationC,
    path: pathlib.Path,
    append: bool=False,
) -> None:
    """Generate the JSON database of default parameter values."""
    obj = {
        'BASETYPES_H': {**basetypes_h.todict('raw')},
        'CONFIGURATION_C': {**configuration_c.todict('raw')},
    }
    sources = {
        str(basetypes_h.origin),
        str(configuration_c.origin),
    }
    if append:
        with path.open('r') as rp:
            loaded = dict(json.load(rp))
        for k, v in obj.items():
            v.update(loaded.get(k, {}))
        if loaded['sources']:
            sources |= set(loaded['sources'])
    with path.open('w') as wp:
        json.dump(obj, wp, indent=4, sort_keys=True)
    srclog = path.parent / 'sources.log'
    _log_json_sources(srclog, sources)


_timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

_SOURCES_LOG_FOOTER = \
f'''This file is unversioned because it contains user-specific paths.
DO NOT commit this file to the repository.
'''


def _log_json_sources(path: pathlib.Path, sources: typing.Iterable[str]):
    """Create a log of the source files used in `_generate_json`."""
    lines = [
        'The following source files',
        '\n\n',
        '\n'.join(sources),
        '\n\n',
        'produced the current versions of',
        '\n\n',
        str(_PY_PATH),
        '\n',
        str(_DB_PATH),
        '\n\n',
        _SOURCES_LOG_FOOTER,
        '\n',
        f'Updated: {_timestr}',
        '\n',
    ]
    with path.open('w') as wp:
        wp.writelines(lines)


_DEFAULT_PY_DOC = \
f'''Default values and metadata for EPREM simulation parameters.

DO NOT EDIT THIS FILE. It was created via the `generate` feature of this module. Run `python </path/to/this/module> generate -h` for more information.
'''


_BASETYPES_H_DOC = \
'''Values and metadata for constants defined in `baseTypes.h`.

Each entry contains the numerical value (`'value'`), a brief description
(`'info'`), the metric unit (`'unit'`), and the built-in type (`'type'`) of each
defined constant.

Notes
-----
* A `'unit'` of `None` implies a non-physical parameter (e.g., a boolean flag or
  system path), whereas a `'unit'` of `'1'` implies a unitless physical
  parameter.

See Also
--------
`~runtime.Defaults`
    A mapping from parameter to default value, with value converted to its
    equivalent built-in type.

`~runtime.Interface`
    An aliased mapping from parameter to user-provided value, if available, or
    default value.
'''


_CONFIGURATION_C_DOC = \
'''Metadata for parameters defined in `configuration.c`.

Each entry contains the default value (`'default'`), the smallest acceptable
value ('`minimum`'), the largest acceptable value ('`maximum`'), as well as the
equivalent built-in type and metric unit of those values (`'type'` and
`'unit'`). Some entries also contain declared aliases for the parameter
('`aliases`').

Notes
-----
* This dictionary stores all values as strings because some values are defined
  with respect to others.
* A `'unit'` of `None` implies a non-physical parameter (e.g., a boolean flag or
  system path), whereas a `'unit'` of `'1'` implies a unitless physical
  parameter.

See Also
--------
`~runtime.Defaults`
    A mapping from parameter to default value, with value converted to its
    equivalent built-in type.

`~runtime.Interface`
    An aliased mapping from parameter to user-provided value, if available, or
    default value.
'''


def _generate_py(
    basetypes_h: BaseTypesH,
    configuration_c: ConfigurationC,
    path: pathlib.Path,
) -> None:
    """Generate the Python module of default parameter values."""
    lines = [
        f'"""\n{_DEFAULT_PY_DOC}"""\n',
        '\n\n',
        f"{basetypes_h.tostring(indent=4, sort=True, mode='full')}\n",
        f'"""{_BASETYPES_H_DOC}"""\n',
        '\n\n',
        f"{configuration_c.tostring(indent=4, sort=True, mode='full')}\n",
        f'"""{_CONFIGURATION_C_DOC}"""\n',
        '\n\n',
    ]
    with path.open('w') as fp:
        fp.writelines(lines)


def run(mode: str, options: typing.Mapping):
    if mode == 'generate':
        return generate_defaults(**options)
    if mode == 'compare':
        return compare_arguments(**options)
    raise CLIError(f"Unknown mode: {mode!r}")


_docstring_replacements = {
    '`src`': 'SRC',
    '`source`': 'SRC',
    "`paths`": "the given paths",
    '`': "'",
    "the local database": str(_DB_PATH),
}

DESCRIPTIONS = {
    'generate': etc.doc2help(
        generate_defaults,
        mode='full',
        replacements=_docstring_replacements,
    ),
    'compare': etc.doc2help(
        compare_arguments,
        mode='full',
        replacements=_docstring_replacements,
    ),
}
