"""
Tests for physical vectors.
"""

import numbers
import operator as standard
import typing

import numpy
import numpy.typing
import pytest

import support
from eprempy import measured
from eprempy import physical
from eprempy import quantity


@pytest.fixture
def array():
    return numpy.array([1.0, 10.0, -5.0])


def test_factory():
    """Test various ways to create a physical vector."""
    value = 2
    unit = 'km'
    vector = physical.vector([value])
    copied = physical.vector(vector)
    assert copied is not vector
    assert copied == vector
    assert numpy.array_equal(vector.data, [value])
    assert vector.unit == '1'
    vector = physical.vector([value], unit=unit)
    assert numpy.array_equal(vector.data, [value])
    assert vector.unit == unit
    scalar = physical.scalar(value, unit=unit)
    vector = physical.vector(scalar)
    assert numpy.array_equal(vector.data, [value])
    assert vector.unit == unit
    tensor = physical.tensor([value, value], unit=unit)
    vector = physical.vector(tensor)
    assert numpy.array_equal(vector.data, [value, value])
    assert vector.unit == unit
    with pytest.raises(TypeError):
        physical.vector(value, unit=unit)
    with pytest.raises(TypeError):
        physical.vector([[value]])
    with pytest.raises(TypeError):
        physical.vector(physical.tensor([[value], [value]]))
    for arg in (scalar, vector):
        with pytest.raises(ValueError):
            physical.scalar(arg, unit=unit)


def test_measure():
    """Test the use of `__measure__` on a physical vector."""
    x = physical.vector([1.5, 3.0, -1.5, -3.0], unit='J / s')
    assert quantity.ismeasurable(x)
    m = quantity.measure(x)
    assert isinstance(m, quantity.Measurement)
    assert m.unit == x.unit
    assert numpy.array_equal(x, m)
    with pytest.raises(TypeError):
        float(m)
    with pytest.raises(TypeError):
        int(m)


def test_len():
    """A vector should have the same length as its data attribute."""
    data = numpy.array([1.5, 3.0, -1.5, -3.0])
    vectors = (
        physical.vector(data),
        physical.vector(data, unit='m / s'),
    )
    for vector in vectors:
        assert len(vector.data) == len(data)


def test_iter():
    """Test the behavior when iterating over a vector."""
    data = numpy.array([1.5, 3.0, -1.5, -3.0])
    unit = 'm / s'
    vector = physical.vector(data, unit=unit)
    for this, x in zip(vector, data):
        assert isinstance(this, physical.Scalar)
        assert this.data == x
        assert this.unit == unit


def test_subscription():
    """Test the behavior of a vector when subscripted."""
    data = numpy.array([1.5, 3.0, -1.5, -3.0])
    original = physical.vector(data, unit='J / s')
    vector = original[1:3]
    assert isinstance(vector, physical.Vector)
    assert numpy.array_equal(vector.data, data[1:3])
    scalar = original[0]
    assert isinstance(scalar, physical.Scalar)
    assert scalar.data == original.data[0]
    assert scalar.unit == original.unit


def test_equality(array: numpy.ndarray):
    """Test equality-based comparative operations on vectors."""
    unit = 'm'
    # the reference vector
    a = physical.vector(array, unit=unit)
    # directly test "equal" via __eq__
    assert a == physical.vector(array, unit=unit)
    unequal = [
        # different values; equal shape; equal unit
        physical.vector([5.0, 10.0, 1.0], unit=unit),
        # equal values; equal shape; different unit
        physical.vector([5.0, 10.0, 1.0], unit='J'),
    ]
    for other in unequal:
        # directly test "not equal" via __ne__
        assert a != other
        # indirectly test "not equal" via __eq__
        assert not (a == other)


def test_ordering(array: numpy.ndarray):
    """Test ordering-based comparative operations on vectors."""
    vx = array
    vy = numpy.array([*array[:2], -array[2]])
    ux = 'm / s'
    uy = 'J'
    # the reference vector
    xx = physical.vector(vx, unit=ux)
    # same unit; same shape
    yx = physical.vector(vy, unit=ux)
    valid = [
        (standard.lt, xx, yx),
        (standard.le, xx, yx),
        (standard.gt, xx, yx),
        (standard.ge, xx, yx),
    ]
    for f, a, b in valid:
        r = f(a.data, b.data)
        assert numpy.array_equal(f(a, b), physical.vector(r))
    # different unit
    yy = physical.vector(vy, unit=uy)
    invalid = [
        (standard.lt, xx, yy),
        (standard.le, xx, yy),
        (standard.gt, xx, yy),
        (standard.ge, xx, yy),
    ]
    for f, a, b in invalid:
        with pytest.raises(ValueError):
            f(a, b)


def test_unary(array: numpy.ndarray):
    """Test unary numerical operations on vectors."""
    unit = 'm'
    vector = physical.vector(array, unit=unit)
    operators = [
        abs,
        standard.pos,
        standard.neg,
    ]
    for f in operators:
        assert f(vector) == physical.vector(f(array), unit=unit)


def test_additive(array: numpy.ndarray) -> None:
    """Test additive operations on physical vectors."""
    meter = 'm'
    joule = 'J'
    original = physical.vector(array, unit=meter)
    sameunit = physical.vector(array, unit=meter)
    valid = [
        # same unit
        (original, sameunit),
    ]
    operators = (standard.add, standard.sub)
    for f in operators:
        for a, b in valid:
            check_additive(f, a, b)
            check_additive(f, b, a)
    diffunit = physical.vector(array, unit=joule)
    invalid = [
        # can't add or subtract vectors with different units
        (diffunit, original),
    ]
    for f in operators:
        for a, b in invalid:
            with pytest.raises(ValueError):
                f(a, b)
            with pytest.raises(ValueError):
                f(b, a)


def check_additive(
    f: typing.Callable,
    a: physical.Vector,
    b: physical.Vector,
) -> None:
    """Helper for `test_additive`."""
    new = f(a, b)
    assert isinstance(new, physical.Vector)
    expected = compute(f, a, b)
    assert numpy.array_equal(new, expected)
    assert new.unit == a.unit


def test_multiplicative(array: numpy.ndarray) -> None:
    """Test multiplicative operations on physical vectors."""
    meter = 'm'
    joule = 'J'
    original = physical.vector(array, unit=meter)
    sameunit = physical.vector(array, unit=meter)
    diffunit = physical.vector(array, unit=joule)
    value = 2.0
    singular = physical.vector([value], unit=meter)
    operators = (
        (standard.mul, standard.mul),
        (standard.truediv, standard.truediv),
        (standard.floordiv, standard.truediv),
        (standard.mod, standard.truediv),
    )
    valid = [
        (original, sameunit),
        (original, diffunit),
        (original, singular),
        (original, value),
        (singular, singular),
    ]
    for f, g in operators:
        for a, b in valid:
            check_multiplicative(f, g, a, b)
            check_multiplicative(f, g, b, a)


def check_multiplicative(
    f: typing.Callable,
    g: typing.Callable,
    a: typing.Union[physical.Vector, numbers.Real],
    b: typing.Union[physical.Vector, numbers.Real],
) -> None:
    """Helper for `test_multiplicative`."""
    new = f(a, b)
    assert isinstance(new, physical.Vector)
    expected = compute(f, a, b)
    assert numpy.array_equal(new, expected)
    if isinstance(a, numbers.Real):
        unit = g('1', b.unit)
    elif isinstance(b, numbers.Real):
        unit = a.unit
    else:
        unit = g(a.unit, b.unit)
    assert new.unit == unit


def test_pow(array: numpy.ndarray) -> None:
    """Test exponentiation on a physical vector."""
    meter = 'm'
    joule = 'J'
    original = physical.vector(array, unit=meter)
    p = 3
    unitless = physical.vector(array)
    valid = [
        # can raise a vector by a number
        (original, p, physical.Vector),
        # can raise a unitless vector by a unitless vector
        (unitless, unitless, physical.Vector),
        # can raise a number by a unitless vector
        (p, unitless, numpy.ndarray),
        # can raise a numpy array by a unitless vector
        (original.data, unitless, numpy.ndarray)
    ]
    for a, b, t in valid:
        check_pow(standard.pow, a, b, t)
    diffunit = physical.vector(array, unit=joule)
    invalid = [
        # a non-numeric exponent is meaningless
        (original, '1', TypeError),
        # cannot raise a unitful vector by even a unitless vector
        (original, unitless, ValueError),
        # cannot raise anything by a unitful vector
        (p, original, ValueError),
        (original.data, original, ValueError),
        (original, original, ValueError),
        (original, diffunit, ValueError),
        (diffunit, original, ValueError),
    ]
    for a, b, error in invalid:
        with pytest.raises(error):
            a ** b


def check_pow(
    f: typing.Callable,
    a: typing.Union[physical.Vector, numbers.Real],
    b: typing.Union[physical.Vector, numbers.Real],
    t: typing.Type[measured.ObjectT]=physical.Vector,
) -> None:
    """Helper for `test_pow`."""
    new = f(a, b)
    assert isinstance(new, t)
    if isinstance(new, physical.Vector):
        expected = compute(f, a, b)
        assert numpy.array_equal(new, expected)
        if a.isunitless:
            assert new.unit == '1'
        else:
            p = b.data if isinstance(b, physical.Object) else b
            assert new.unit == f(a.unit, p)


def compute(
    f: typing.Callable,
    a: typing.Union[physical.Vector, typing.SupportsFloat],
    b: typing.Union[physical.Vector, typing.SupportsFloat],
) -> numpy.ndarray:
    """Compute the result of `f(a, b)`."""
    if all(not isinstance(i, physical.Vector) for i in (a, b)):
        raise TypeError("Expected at least one of a or b to be a vector")
    if isinstance(b, typing.SupportsFloat):
        return f(a.data, float(b))
    if isinstance(a, typing.SupportsFloat):
        return f(float(a), b.data)
    return f(a.data, b.data)


def test_trig(array: numpy.ndarray):
    """Test `numpy` trigonometric ufuncs on a physical vector."""
    for f in (numpy.sin, numpy.cos, numpy.tan):
        for unit in {'rad', 'deg'}:
            old = physical.vector(array, unit=unit)
            new = f(old)
            assert isinstance(new, physical.Vector)
            assert numpy.array_equal(new, f(old.data))
            assert new.unit == '1'
        bad = physical.vector(array, unit='m')
        with pytest.raises(ValueError):
            f(bad)


def test_sqrt(array: numpy.ndarray):
    """Test `numpy.sqrt` on a physical vector."""
    data = abs(array)
    old = physical.vector(data, unit='m')
    new = numpy.sqrt(old)
    assert isinstance(new, physical.Vector)
    assert numpy.array_equal(new, numpy.sqrt(data))
    assert new.unit == f"{old.unit}^1/2"


def test_squeeze(array: numpy.ndarray):
    """Test `numpy.squeeze` on a physical vector."""
    old = physical.vector(array, unit='m')
    new = numpy.squeeze(old)
    assert isinstance(new, physical.Vector)
    assert numpy.array_equal(new, numpy.squeeze(array))
    assert new.unit == old.unit
    singular = physical.vector([2.0], unit='m')
    scalar = numpy.squeeze(singular)
    assert isinstance(scalar, physical.Scalar)
    assert scalar.unit == singular.unit


def test_mean(array: numpy.ndarray):
    """Test `numpy.mean` of a physical vector."""
    old = physical.vector(array, unit='m')
    new = numpy.mean(old)
    assert isinstance(new, physical.Scalar)
    assert numpy.array_equal(new.data, numpy.mean(array))
    assert new.unit == old.unit


def test_sum(array: numpy.ndarray):
    """Test `numpy.sum` of a physical vector."""
    old = physical.vector(array, unit='m')
    new = numpy.sum(old)
    assert isinstance(new, physical.Scalar)
    assert numpy.array_equal(new.data, numpy.sum(array))
    assert new.unit == old.unit


def test_cumsum(array: numpy.ndarray):
    """Test `numpy.cumsum` of a physical vector."""
    old = physical.vector(array, unit='m')
    new = numpy.cumsum(old)
    assert isinstance(new, physical.Vector)
    assert numpy.array_equal(new.data, numpy.cumsum(array))
    assert new.unit == old.unit


def test_transpose(array: numpy.ndarray):
    """Test `numpy.transpose` on a physical vector."""
    old = physical.vector(array, unit='cm')
    new = numpy.transpose(old)
    assert isinstance(new, physical.Vector)
    assert numpy.array_equal(new.data, numpy.transpose(array))
    assert new.unit == old.unit


def test_gradient(array: numpy.ndarray):
    """Test `numpy.gradient` on a physical vector."""
    vector = physical.vector(array, unit='m')
    cases = [
        {
            'dt': [],
            'unit': vector.unit,
            'reference': numpy.gradient(array),
        },
        {
            'dt': [0.5],
            'unit': vector.unit,
            'reference': numpy.gradient(array, 0.5),
        },
        {
            'dt': [physical.scalar(0.5, unit='s')],
            'unit': vector.unit / 's',
            'reference': numpy.gradient(array, 0.5),
        },
    ]
    for case in cases:
        dt = case.get('dt', [])
        gradient = numpy.gradient(vector, *dt, axis=case.get('axis'))
        computed = gradient if isinstance(gradient, list) else [gradient]
        reference = case['reference']
        expected = reference if isinstance(reference, list) else [reference]
        unit = case['unit']
        for this, that in zip(computed, expected):
            assert isinstance(this, physical.Vector)
            assert numpy.array_equal(this, that)
            assert this.unit == unit


def test_unit():
    """Test the ability to update a physical vector's unit."""
    old = physical.vector([2.0, 4.0], 'm')
    new = old.withunit('km')
    assert isinstance(new, type(old))
    assert new is not old
    assert new.unit == 'km'
    factor = old.unit >> new.unit
    assert numpy.array_equal(new, factor*numpy.array(old))
    with pytest.raises(ValueError):
        old.withunit('J')


