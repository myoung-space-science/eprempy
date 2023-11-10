import typing

import math

import numpy
import numpy.typing
import pytest

from eprempy import numeric
from eprempy import parameter
from eprempy import physical


def test_variable_factory():
    """Test various ways to create a physical variable."""
    value = -2
    variable = parameter.variable(value)
    copied = parameter.variable(variable)
    assert copied is not variable
    assert copied == variable
    assert isinstance(variable, parameter.Variable)
    assert variable.data == value
    assert variable.unit == '1'
    variable = parameter.variable([value])
    assert isinstance(variable, parameter.Variable)
    assert numpy.array_equal(variable.data, [value])
    assert variable.unit == '1'
    unit = 'km'
    variable = parameter.variable(value, unit=unit)
    assert isinstance(variable, parameter.Variable)
    assert variable.data == value
    assert variable.unit == unit
    variable = parameter.variable([value], unit=unit)
    assert isinstance(variable, parameter.Variable)
    assert numpy.array_equal(variable.data, [value])
    assert variable.unit == unit
    scalar = physical.scalar(value, unit=unit)
    tensor = physical.tensor([value], unit=unit)
    for arg in (scalar, tensor, variable):
        with pytest.raises(ValueError):
            parameter.variable(arg, unit=unit)


def test_variable_subscription():
    """Test the subscription behavior of a physical variable."""
    values = [1.0, 2.0, 3.0]
    unit = 'J'
    v = parameter.variable(values, unit=unit)
    assert v[:2] == parameter.variable(values[:2], unit=unit)
    assert v[0] == physical.scalar(values[0], unit=unit)


def test_singular_variable():
    """Test functions on a single-valued physical variable."""
    value = 1.5
    unit = 'm'
    types = [
        int,
        float,
        complex,
    ]
    for t in types:
        for arg in (value, [value]):
            x = parameter.variable(arg, unit=unit)
            assert t(x) == t(value)
    operators = [
        round,
        math.floor,
        math.ceil,
        math.trunc,
    ]
    for f in operators:
        for arg in (value, [value]):
            x = parameter.variable(arg, unit=unit)
            assert f(x) == physical.scalar(f(value), unit=unit)


def test_interface(
    srcdir: str,
    config: typing.Dict[str, typing.Dict[str, dict]],
    reference: typing.Dict[str, dict],
) -> None:
    """Test the full interface to EPREM parameter values.
    
    After creating an instance of `parameter.Interface` with a known EPREM
    configuration file, this test will
    
    * check that the interface contains all the parameters in `reference`,
      regardless of value
    * compare each parameter value in the interface, whether default or
      user-provided, to the value in the configuration file.
    """
    for cfg in config.values():
        interface = parameter.interface(srcdir=srcdir, config=cfg['path'])
        for key, value in reference.items():
            expected = cfg['args'].get(key, value['default'])
            for alias in parameter.ALIASES.get(key, [key]):
                assert alias in interface
                assert numerically_equal(interface[key], expected)


def numerically_equal(x, y) -> bool:
    """Helper for `~test_interface`.
    
    This function returns a single truth value indicating whether the arguments
    are numerically equal, after choosing an appropriate equality test based on
    the type of `x`.
    """
    if not isinstance(x, parameter.Variable):
        return x == y
    if x.size == 1:
        return x.data[0] == y
    return numeric.data.isequal(x, y)


