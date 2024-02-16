"""
Support for working with EPREM simulation parameters.
"""

import typing

from .. import metric
from .. import paths
from .. import physical
from .. import quantity
from .. import real
from ._config import (
    ConfigFile,
    configfile_factory as configfile,
    Defaults,
    defaults_factory as defaults,
)
from ._metadata import (
    ALIASES,
)
from ._runtime import (
    Interface,
    Variable,
)
from ._src import (
    BaseTypesH,
    ConfigurationC,
    SourceFile,
)
from . import reference


DB_PATH = str(SourceFile._db_path)
"""Public string version of source file default database path."""


__all__ = [
    "ALIASES",
    "BaseTypesH",
    "ConfigurationC",
    "ConfigFile",
    "Defaults",
    "Interface",
    "SourceFile",
    "Variable",
    "configfile",
    "defaults",
    "reference",
    "interface",
    "variable",
]


ArgumentType = typing.Union[physical.Scalar, physical.Tensor]


@typing.overload
def variable(
    x: typing.Any,
    /,
    unit: typing.Optional[metric.UnitLike],
) -> _runtime.Variable:
    """Create a variable from the given arguments, if possible"""

@typing.overload
def variable(
    x: typing.Sequence[real.ValueType],
    /,
) -> _runtime.Variable[real.ValueType]:
    """Create a unitless variable from a real-valued sequence.

    Parameters
    ----------
    x : sequence of `int`, `float`, or `numbers.Real`
        The numeric value(s) of the new variable. This function will convert the
        given sequence to a `numpy.ndarray` if necessary.

    Returns
    -------
    `~Variable`
        A new variable with the given value(s), and a unit equal to
        '1'.

    Raises
    ------
    `TypeError`
        The input is not logically 1-dimensional.
    """

@typing.overload
def variable(
    x: typing.Sequence[real.ValueType],
    /,
    unit: metric.UnitLike,
) -> _runtime.Variable[real.ValueType]:
    """Create a variable from a real-valued sequence and a unit.

    Parameters
    ----------
    x : sequence of `int`, `float`, or `numbers.Real`
        The numeric value(s) of the new variable. This function will convert the
        given sequence to a `numpy.ndarray` if necessary.
    unit : unit-like
        The metric unit associated with `x`.

    Returns
    -------
    `~Variable`
        A new variable with the given value(s) and unit.

    Raises
    ------
    `TypeError`
        The input is not logically 1-dimensional.
    """

@typing.overload
def variable(
    x: _runtime.Variable[real.ValueType],
    /,
) -> _runtime.Variable[real.ValueType]:
    """Create a variable from an existing variable.

    Parameters
    ----------
    x : `~Variable`
        The variable from which to create a new variable. This function will
        make a copy of `x`.

    Returns
    -------
    `~Variable`
        A new variable with value and unit taken from the given
        variable.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

@typing.overload
def variable(
    x: physical.Scalar[real.ValueType],
    /,
) -> _runtime.Variable[real.ValueType]:
    """Create a variable from a physical scalar.

    Parameters
    ----------
    x : `~physical.Scalar`
        The scalar from which to create a new variable. This function will
        convert the scalar's data value into a 1-element `numpy.ndarray`.

    Returns
    -------
    `~Variable`
        A new variable with value and unit taken from the given scalar.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

@typing.overload
def variable(
    x: physical.Vector[real.ValueType],
    /,
) -> _runtime.Variable[real.ValueType]:
    """Create a variable from a physical vector.

    Parameters
    ----------
    x : `~physical.Vector`
        The vector from which to create a new variable.

    Returns
    -------
    `~Variable`
        A new variable with value and unit taken from the given vector.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

@typing.overload
def variable(
    x: quantity.Measurement[real.ValueType],
    /,
) -> _runtime.Variable[real.ValueType]:
    """Create a variable from an existing measurement.

    Parameters
    ----------
    x : `~quantity.Measurement`
        The measurement from which to create a new variable. This function will
        convert the measurement's data into a `numpy.ndarray` if necessary.

    Returns
    -------
    `~Variable`
        A new variable with data and unit taken from the given
        measurement.

    Raises
    ------
    `ValueError`
        The caller passed an explicit unit.
    """

def variable(x, /, unit=None):
    return _runtime.variable_factory(x, unit=unit)


@typing.overload
def interface(
    config: typing.Optional[paths.PathLike]=None,
    srcdir: typing.Optional[paths.PathLike]=None,
    **options
) -> Interface:
    """Create an interface to EPREM parameter values.

    Parameters
    ----------
    config : path-like, optional
        The location of the EPREM configuration file containing user-provided
        parameter values for a particular EPREM simulation run. May be omitted,
        in which case the interface will use default argument values.

    srcdir : path-like, optional
        The directory containing EPREM `configuration.c`. May be omitted, in
        which case the interface will use pre-computed values.

    **options
        Options for loading the configuration file. See `~ConfigFile`
        for more information.

    Notes
    -----
    - Path-like arguments may be any path-like object (e.g., `str`,
      `pathlib.Path`), may be relative, and may contain standard wildcard
      characters (e.g., `~`).
    """

def interface(*args, **kwargs):
    return _runtime.interface_factory(*args, **kwargs)


