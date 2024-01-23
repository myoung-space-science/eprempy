"""
Tests for physical scalars.
"""

import math
import numbers
import operator as standard
import typing

import numpy
import numpy.typing
import pytest

from eprempy import measured
from eprempy import metric
from eprempy import numeric
from eprempy import physical
from eprempy import quantity


def test_scalar_factory():
    """Test various ways to create a physical scalar."""
    value = 2
    unit = 'km'
    scalar = physical.scalar(value)
    copied = physical.scalar(scalar)
    assert copied is not scalar
    assert copied == scalar
    assert scalar.data == value
    assert scalar.unit == '1'
    scalar = physical.scalar(value, unit=unit)
    assert scalar.data == value
    assert scalar.unit == unit
    for arg in ([1], numpy.array([1])):
        scalar = physical.scalar(arg, unit=unit)
        assert scalar.data == numpy.array(arg)
        assert scalar.unit == unit
    for arg in ([1, 2], numpy.array([1, 2])):
        with pytest.raises(TypeError):
            physical.scalar(arg)
    tensor = physical.tensor([value], unit=unit)
    for arg in (scalar, tensor):
        with pytest.raises(ValueError):
            physical.scalar(arg, unit=unit)


def test_measure_scalar():
    """Test the use of `__measure__` on a physical scalar."""
    x = physical.scalar(1.5, unit='J / s')
    assert quantity.ismeasurable(x)
    m = quantity.measure(x)
    assert isinstance(m, quantity.Measurement)
    assert m.unit == x.unit
    assert float(m) == float(x)
    assert int(m) == int(x)


def test_scalar_additive():
    """Test additive operations on physical scalars."""
    va = 2.0
    vb = 1.1
    meter = 'm'
    original = physical.scalar(va, unit=meter)
    sameunit = physical.scalar(vb, unit=meter)
    unitless = physical.scalar(vb)
    valid = [
        # measurable tuple with same unit
        (original, (vb, original.unit), original.unit),
        # scalar with same unit
        (original, sameunit, original.unit),
        # plain number with unitless scalar
        (unitless, vb, '1'),
    ]
    operators = (standard.add, standard.sub)
    for f in operators:
        for a, b, u in valid:
            check_scalar_additive(f, a, b, u)
            check_scalar_additive(f, b, a, u)
    joule = 'J'
    diffunit = physical.scalar(va, unit=joule)
    invalid = [
        # can't add or subtract objects with a different unit
        (original, (vb, joule), ValueError),
        (original, diffunit, ValueError),
        # can't add or subtract plain numbers from a unitful scalar
        (original, va, TypeError),
    ]
    for f in operators:
        for a, b, err in invalid:
            with pytest.raises(err):
                f(a, b)
            with pytest.raises(err):
                f(b, a)


def check_scalar_additive(f, a, b, unit: metric.UnitLike) -> None:
    """Helper for `test_scalar_additive`."""
    new = f(a, b)
    assert isinstance(new, physical.Scalar)
    x = quantity.getdata(a)
    y = quantity.getdata(b)
    assert new.data == f(x, y)
    assert new.unit == unit


def test_scalar_multiplicative():
    """Test multiplicative operations on physical scalars."""
    va = 2.0
    vb = 1.1
    meter = 'm'
    joule = 'J'
    original = physical.scalar(va, unit=meter)
    sameunit = physical.scalar(vb, unit=meter)
    diffunit = physical.scalar(va, unit=joule)
    valid = [
        # same unit
        (original, sameunit),
        (original, (vb, original.unit)),
        # different unit
        (original, diffunit),
        # scale by constant factor
        (original, va),
    ]
    operators = (
        (standard.mul, standard.mul),
        (standard.truediv, standard.truediv),
        (standard.floordiv, standard.truediv),
        (standard.mod, standard.truediv),
    )
    for f, g in operators:
        for a, b in valid:
            check_scalar_multiplicative(f, g, a, b)
            check_scalar_multiplicative(f, g, b, a)


def check_scalar_multiplicative(
    f: typing.Callable,
    g: typing.Callable,
    a: typing.Union[physical.Scalar, numbers.Real, tuple],
    b: typing.Union[physical.Scalar, numbers.Real, tuple],
) -> None:
    """Helper for `test_scalar_multiplicative`."""
    new = f(a, b)
    assert isinstance(new, physical.Scalar)
    x = quantity.getdata(a)
    y = quantity.getdata(b)
    assert new.data == f(x, y)
    unit = get_scalar_multiplicative_unit(g, a, b)
    assert new.unit == unit


def get_scalar_multiplicative_unit(f, a, b):
    """Helper for `check_scalar_multiplicative`."""
    if isinstance(a, physical.Scalar) and isinstance(b, physical.Scalar):
        return f(a.unit, b.unit)
    if isinstance(a, numbers.Real) and isinstance(b, physical.Scalar):
        return f('1', b.unit)
    if isinstance(a, physical.Scalar) and isinstance(b, numbers.Real):
        return a.unit
    if isinstance(a, tuple) and isinstance(b, physical.Scalar):
        return f(a[-1], b.unit)
    if isinstance(a, physical.Scalar) and isinstance(b, tuple):
        return f(a.unit, b[-1])
    raise TypeError(a, b)


def test_scalar_pow():
    """Test exponentiation on a physical scalar."""
    va = 2.0
    vb = 1.1
    meter = 'm'
    joule = 'J'
    original = physical.scalar(va, unit=meter)
    sameunit = physical.scalar(vb, unit=meter)
    diffunit = physical.scalar(va, unit=joule)
    p = 3
    unitless = physical.scalar(p)
    valid = [
        # raise a scalar by a number
        (original, p, physical.Scalar),
        # raise a scalar by a unitless scalar
        (original, unitless, physical.Scalar),
        # raise a number by a unitless scalar
        (p, unitless, type(p)),
    ]
    for a, b, t in valid:
        check_scalar_pow(standard.pow, a, b, t)
    invalid = [
        # a non-numeric exponent is meaningless
        (original, '1', TypeError),
        # can't raise anything by a unitful scalar
        (p, original, ValueError),
        (unitless, original, ValueError),
        (original, sameunit, ValueError),
        (sameunit, original, ValueError),
        (original, diffunit, ValueError),
        (diffunit, original, ValueError),
    ]
    for a, b, error in invalid:
        with pytest.raises(error):
            a ** b


def check_scalar_pow(
    f,
    a: typing.Union[physical.Scalar, numbers.Real],
    b: typing.Union[physical.Scalar, numbers.Real],
    t: typing.Type[measured.ObjectT]=physical.Scalar,
) -> None:
    """Helper for `test_scalar_pow`."""
    new = f(a, b)
    assert isinstance(new, t)
    if t == physical.Scalar:
        x = a.data if isinstance(a, physical.Scalar) else a
        y = b.data if isinstance(b, physical.Scalar) else b
        assert new.data == f(x, y)
        p = b.data if isinstance(b, physical.Scalar) else b
        assert new.unit == f(a.unit, p)


def test_scalar_int():
    """Test the conversion to `int` for a physical scalar."""
    assert int(physical.scalar(1.1, unit='m')) == 1


def test_scalar_float():
    """Test the conversion to `float` for a physical scalar."""
    assert int(physical.scalar(1, unit='m')) == 1.0


def test_scalar_round():
    """Test the built-in `round` method on a physical scalar."""
    values = [
        -1.6,
        -1.1,
        +1.1,
        +1.6,
    ]
    unit = 'm'
    for value in values:
        a = physical.scalar(value, unit=unit)
        r = round(a)
        assert isinstance(r, physical.Scalar)
        assert r.data == round(value)
        assert r.unit == metric.unit(unit)


def test_scalar_floor():
    """Test the `math.floor` method on a physical scalar."""
    values = [
        -1.6,
        -1.1,
        +1.1,
        +1.6,
    ]
    unit = 'm'
    for value in values:
        a = physical.scalar(value, unit=unit)
        r = math.floor(a)
        assert isinstance(r, physical.Scalar)
        assert r.data == math.floor(value)
        assert r.unit == metric.unit(unit)


def test_scalar_ceil():
    """Test the `math.ceil` method on a physical scalar."""
    values = [
        -1.6,
        -1.1,
        +1.1,
        +1.6,
    ]
    unit = 'm'
    for value in values:
        a = physical.scalar(value, unit=unit)
        r = math.ceil(a)
        assert isinstance(r, physical.Scalar)
        assert r.data == math.ceil(value)
        assert r.unit == metric.unit(unit)


def test_scalar_trunc():
    """Test the `math.trunc` method on a physical scalar."""
    values = [
        -1.6,
        -1.1,
        +1.1,
        +1.6,
    ]
    unit = 'm'
    for value in values:
        a = physical.scalar(value, unit=unit)
        r = math.trunc(a)
        assert isinstance(r, physical.Scalar)
        assert r.data == math.trunc(value)
        assert r.unit == metric.unit(unit)


def test_scalar_trig():
    """Test `numpy` trigonometric ufuncs on a physical scalar."""
    value = 1.0
    for f in (numpy.sin, numpy.cos, numpy.tan):
        for unit in {'rad', 'deg'}:
            old = physical.scalar(value, unit=unit)
            new = f(old)
            assert isinstance(new, physical.Scalar)
            assert numeric.data.isequal(new, f(old.data))
            assert new.unit == '1'
        bad = physical.scalar(value, unit='m')
        with pytest.raises(ValueError):
            f(bad)


def test_scalar_sqrt():
    """Test `numpy.sqrt` on a physical scalar."""
    scalar = physical.scalar(2.0, unit='m')
    value = numpy.sqrt(scalar.data)
    unit = scalar.unit ** 0.5
    assert numpy.sqrt(scalar) == physical.scalar(value, unit=unit)


def test_scalar_squeeze():
    """Test `numpy.squeeze` on a physical scalar."""
    value = 4
    old = physical.scalar(value, unit='m')
    new = numpy.squeeze(old)
    assert new is old


def test_scalar_mean():
    """Test `numpy.mean` of a physical scalar."""
    value = 2
    old = physical.scalar(value, unit='m')
    new = numpy.mean(old)
    assert new is not old
    assert isinstance(new, physical.Scalar)
    assert numpy.array_equal(new.data, numpy.mean(value))
    assert new.unit == old.unit


def test_scalar_sum():
    """Test `numpy.sum` of a physical scalar."""
    value = 2
    old = physical.scalar(value, unit='m')
    new = numpy.sum(old)
    assert new is not old
    assert isinstance(new, physical.Scalar)
    assert numpy.array_equal(new.data, numpy.sum(value))
    assert new.unit == old.unit


def test_scalar_cumsum():
    """Test `numpy.cumsum` of a physical scalar."""
    value = 2
    old = physical.scalar(value, unit='m')
    new = numpy.cumsum(old)
    assert isinstance(new, physical.Vector)
    assert new.size == 1
    assert numpy.array_equal(new.data, numpy.cumsum(value))
    assert new.unit == old.unit


def test_scalar_transpose():
    """Test `numpy.transpose` on a physical scalar."""
    value = 2
    old = physical.scalar(value, unit='cm')
    new = numpy.transpose(old)
    assert new is not old
    assert new == physical.scalar(value, unit='cm')


def test_scalar_gradient():
    """Test `numpy.gradient` on a physical scalar."""
    value = 2
    scalar = physical.scalar(value, unit='cm')
    assert numpy.gradient(scalar) == []


def test_scalar_unit():
    """Test the ability to update a physical scalar's unit."""
    old = physical.scalar(2.0, 'm')
    new = old.withunit('km')
    assert isinstance(new, type(old))
    assert new is not old
    assert new.unit == 'km'
    factor = old.unit >> new.unit
    assert float(new) == float(factor*old)
    with pytest.raises(ValueError):
        old.withunit('J')


