"""
Tests for physical tensors.
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


def test_factory():
    """Test various ways to create a physical tensor."""
    value = 2
    unit = 'km'
    tensor = physical.tensor([value])
    copied = physical.tensor(tensor)
    assert copied is not tensor
    assert copied == tensor
    assert numpy.array_equal(tensor.data, [value])
    assert tensor.unit == '1'
    tensor = physical.tensor([value], unit=unit)
    assert numpy.array_equal(tensor.data, [value])
    assert tensor.unit == unit
    scalar = physical.scalar(value, unit=unit)
    tensor = physical.tensor(scalar)
    assert numpy.array_equal(tensor.data, [value])
    assert tensor.unit == unit
    with pytest.raises(TypeError):
        physical.tensor(value, unit=unit)
    for arg in (scalar, tensor):
        with pytest.raises(ValueError):
            physical.scalar(arg, unit=unit)


def test_measure():
    """Test the use of `__measure__` on a physical tensor."""
    x = physical.tensor([[1.5, 3.0], [-1.5, -3.0]], unit='J / s')
    assert quantity.ismeasurable(x)
    m = quantity.measure(x)
    assert isinstance(m, quantity.Measurement)
    assert m.unit == x.unit
    for i in range(2):
        for j in range(2):
            assert m[i, j] == x[i, j]
    with pytest.raises(TypeError):
        float(m)
    with pytest.raises(TypeError):
        int(m)


def test_len():
    """A tensor should have the same length as its data attribute."""
    arrays = (
        numpy.array([1.5, 3.0, -1.5, -3.0]),
        numpy.array([[1.5, 3.0, -1.5, -3.0]]),
        numpy.array([[1.5, 3.0], [-1.5, -3.0]]),
        numpy.array([[1.5], [3.0], [-1.5], [-3.0]]),
    )
    for array in arrays:
        unitless = physical.tensor(array)
        assert len(unitless.data)
        unitful = physical.tensor(array, unit='m / s')
        assert len(unitful.data)


def test_iter():
    """Test the behavior when iterating over a tensor."""
    arrays = (
        numpy.array([1.5, 3.0, -1.5, -3.0]),
        numpy.array([[1.5, 3.0, -1.5, -3.0]]),
        numpy.array([[1.5, 3.0], [-1.5, -3.0]]),
        numpy.array([[1.5], [3.0], [-1.5], [-3.0]]),
    )
    unit = 'm / s'
    for array in arrays:
        tensor = physical.tensor(array, unit=unit)
        for this, x in zip(tensor, array.flat):
            assert isinstance(this, physical.Scalar)
            assert this.data == x
            assert this.unit == unit


def test_subscription():
    """Test the behavior of a tensor when subscripted."""
    data = numpy.array([[1.5, 3.0], [-1.5, -3.0]])
    original = physical.tensor(data, unit='J / s')
    args = [
        (0, slice(None)),
        (slice(None), 0),
    ]
    for arg in args:
        tensor = original[arg]
        assert isinstance(tensor, physical.Tensor)
        assert numpy.array_equal(tensor.data, data[arg])
    scalar = original[0, 0]
    assert isinstance(scalar, physical.Scalar)
    assert scalar.data == original.data[0, 0]
    assert scalar.unit == original.unit


def test_equality():
    """Test equality-based comparative operations on tensors."""
    unit = 'm'
    # the reference tensor
    a = physical.tensor([[1.0], [10.0], [5.0]], unit=unit)
    # directly test "equal" via __eq__
    assert a == physical.tensor([[1.0], [10.0], [5.0]], unit=unit)
    unequal = [
        # different values; equal shape; equal unit
        physical.tensor([[5.0], [10.0], [1.0]], unit=unit),
        # equal values; different shape; equal unit
        physical.tensor([1.0, 10.0, 5.0], unit=unit),
        # equal values; equal shape; different unit
        physical.tensor([[1.0], [10.0], [5.0]], unit='J'),
    ]
    for other in unequal:
        # directly test "not equal" via __ne__
        assert a != other
        # indirectly test "not equal" via __eq__
        assert not (a == other)


def test_ordering():
    """Test ordering-based comparative operations on tensors."""
    vx = numpy.array([[1.0], [10.0], [5.0]])
    vy = numpy.array([[5.0], [10.0], [1.0]])
    vz = vx[:, 0]
    vw = numpy.array([[5.0, 10.0], [1.0, 5.0]])
    ux = 'm / s'
    uy = 'J'
    # the reference tensor
    xx = physical.tensor(vx, unit=ux)
    # same unit; same shape
    yx = physical.tensor(vy, unit=ux)
    # same unit; data will broadcast
    zx = physical.tensor(vz, unit=ux)
    valid = [
        (standard.lt, xx, yx),
        (standard.le, xx, yx),
        (standard.gt, xx, yx),
        (standard.ge, xx, yx),
        (standard.lt, xx, zx),
        (standard.le, xx, zx),
        (standard.gt, xx, zx),
        (standard.ge, xx, zx),
    ]
    for f, a, b in valid:
        r = f(a.data, b.data)
        assert numpy.array_equal(f(a, b), physical.tensor(r))
    # different unit
    yy = physical.tensor(vy, unit=uy)
    # data will not broadcast
    wx = physical.tensor(vw, unit=ux)
    invalid = [
        (standard.lt, xx, yy),
        (standard.le, xx, yy),
        (standard.gt, xx, yy),
        (standard.ge, xx, yy),
        (standard.lt, xx, wx),
        (standard.le, xx, wx),
        (standard.gt, xx, wx),
        (standard.ge, xx, wx),
    ]
    for f, a, b in invalid:
        with pytest.raises(ValueError):
            f(a, b)


def test_unary(ndarrays: support.NDArrays):
    """Test unary numerical operations on tensors."""
    data = ndarrays.r
    unit = 'm'
    tensor = physical.tensor(data, unit=unit)
    operators = [
        abs,
        standard.pos,
        standard.neg,
    ]
    for f in operators:
        assert f(tensor) == physical.tensor(f(data), unit=unit)


def test_additive(ndarrays: support.NDArrays) -> None:
    """Test additive operations on physical tensors."""
    meter = 'm'
    joule = 'J'
    original = physical.tensor(ndarrays.r, unit=meter)
    samedims = physical.tensor(ndarrays.xy, unit=meter)
    valid = [
        # same unit; same dimensions
        (original, samedims),
    ]
    operators = (standard.add, standard.sub)
    for f in operators:
        for a, b in valid:
            check_additive(f, a, b)
            check_additive(f, b, a)
    sharedim = physical.tensor(ndarrays.yz, unit=meter)
    diffdims = physical.tensor(ndarrays.zw, unit=meter)
    diffunit = physical.tensor(ndarrays.r, unit=joule)
    invalid = [
        # can't add or subtract tensors with different dimensions
        (sharedim, original),
        (diffdims, original),
        # can't add or subtract tensors with different units
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
    a: physical.Tensor,
    b: physical.Tensor,
) -> None:
    """Helper for `test_additive`."""
    new = f(a, b)
    assert isinstance(new, physical.Tensor)
    expected = compute(f, a, b)
    assert numpy.array_equal(new, expected)
    assert new.unit == a.unit


def test_multiplicative(ndarrays: support.NDArrays) -> None:
    """Test multiplicative operations on physical tensors."""
    meter = 'm'
    joule = 'J'
    original = physical.tensor(ndarrays.r, unit=meter)
    samedims = physical.tensor(ndarrays.xy, unit=meter)
    sharedim = physical.tensor(ndarrays.yz, unit=meter)
    diffdims = physical.tensor(ndarrays.zw, unit=meter)
    diffunit = physical.tensor(ndarrays.r, unit=joule)
    extradim = physical.tensor(ndarrays.xyz, unit=meter)
    value = 2.0
    singular = physical.tensor([[value]], unit=meter)
    operators = (
        (standard.mul, standard.mul),
        (standard.truediv, standard.truediv),
        (standard.floordiv, standard.truediv),
        (standard.mod, standard.truediv),
    )
    valid = [
        (original, samedims),
        (original, diffunit),
        (extradim, sharedim),
        (original, singular),
        (original, value),
        (singular, singular),
    ]
    for f, g in operators:
        for a, b in valid:
            check_multiplicative(f, g, a, b)
            check_multiplicative(f, g, b, a)
    invalid = [
        (original, sharedim, ValueError),
        (original, extradim, ValueError),
        (original, diffdims, ValueError),
        (samedims, sharedim, ValueError),
        (samedims, extradim, ValueError),
        (samedims, diffdims, ValueError),
        (extradim, diffdims, ValueError),
        (diffdims, sharedim, ValueError),
    ]
    for f, _ in operators:
        for a, b, error in invalid:
            with pytest.raises(error):
                f(a, b)
            with pytest.raises(error):
                f(b, a)


def check_multiplicative(
    f: typing.Callable,
    g: typing.Callable,
    a: typing.Union[physical.Tensor, numbers.Real],
    b: typing.Union[physical.Tensor, numbers.Real],
) -> None:
    """Helper for `test_multiplicative`."""
    new = f(a, b)
    assert isinstance(new, physical.Tensor)
    expected = compute(f, a, b)
    assert numpy.array_equal(new, expected)
    if isinstance(a, numbers.Real):
        unit = g('1', b.unit)
    elif isinstance(b, numbers.Real):
        unit = a.unit
    else:
        unit = g(a.unit, b.unit)
    assert new.unit == unit


def test_pow(ndarrays: support.NDArrays) -> None:
    """Test exponentiation on a physical tensor."""
    meter = 'm'
    joule = 'J'
    original = physical.tensor(ndarrays.r, unit=meter)
    p = 3
    unitless = physical.tensor(ndarrays.r)
    valid = [
        # can raise a tensor by a number
        (original, p, physical.Tensor),
        # can raise a unitless tensor by a unitless tensor
        (unitless, unitless, physical.Tensor),
        # can raise a number by a unitless tensor
        (p, unitless, numpy.ndarray),
        # can raise a numpy array by a unitless tensor
        (original.data, unitless, numpy.ndarray)
    ]
    for a, b, t in valid:
        check_pow(standard.pow, a, b, t)
    samedims = physical.tensor(ndarrays.xy, unit=meter)
    sharedim = physical.tensor(ndarrays.yz, unit=meter)
    diffdims = physical.tensor(ndarrays.zw, unit=meter)
    diffunit = physical.tensor(ndarrays.r, unit=joule)
    extradim = physical.tensor(ndarrays.xyz, unit=meter)
    invalid = [
        # a non-numeric exponent is meaningless
        (original, '1', TypeError),
        # cannot raise a unitful tensor by even a unitless tensor
        (original, unitless, ValueError),
        # cannot raise anything by a unitful tensor
        (p, original, ValueError),
        (original.data, original, ValueError),
        (original, samedims, ValueError),
        (samedims, original, ValueError),
        (original, sharedim, ValueError),
        (sharedim, original, ValueError),
        (original, diffdims, ValueError),
        (diffdims, original, ValueError),
        (original, diffunit, ValueError),
        (diffunit, original, ValueError),
        (original, extradim, ValueError),
        (extradim, original, ValueError),
    ]
    for a, b, error in invalid:
        with pytest.raises(error):
            a ** b


def check_pow(
    f: typing.Callable,
    a: typing.Union[physical.Tensor, numbers.Real],
    b: typing.Union[physical.Tensor, numbers.Real],
    t: typing.Type[measured.ObjectT]=physical.Tensor,
) -> None:
    """Helper for `test_pow`."""
    new = f(a, b)
    assert isinstance(new, t)
    if isinstance(new, physical.Tensor):
        expected = compute(f, a, b)
        assert numpy.array_equal(new, expected)
        if a.isunitless:
            assert new.unit == '1'
        else:
            p = b.data if isinstance(b, physical.Object) else b
            assert new.unit == f(a.unit, p)


def compute(
    f: typing.Callable,
    a: typing.Union[physical.Tensor, typing.SupportsFloat],
    b: typing.Union[physical.Tensor, typing.SupportsFloat],
) -> numpy.ndarray:
    """Compute the result of `f(a, b)`."""
    if all(not isinstance(i, physical.Tensor) for i in (a, b)):
        raise TypeError("Expected at least one of a or b to be a tensor")
    if isinstance(b, typing.SupportsFloat):
        return f(a.data, float(b))
    if isinstance(a, typing.SupportsFloat):
        return f(float(a), b.data)
    return f(a.data, b.data)


def test_trig(ndarrays: support.NDArrays):
    """Test `numpy` trigonometric ufuncs on a physical tensor."""
    for f in (numpy.sin, numpy.cos, numpy.tan):
        for unit in {'rad', 'deg'}:
            old = physical.tensor(
                ndarrays.r,
                unit=unit,
            )
            new = f(old)
            assert isinstance(new, physical.Tensor)
            assert numpy.array_equal(new, f(old.data))
            assert new.unit == '1'
        bad = physical.tensor(
            ndarrays.r,
            unit='m',
        )
        with pytest.raises(ValueError):
            f(bad)


def test_sqrt(ndarrays: support.NDArrays):
    """Test `numpy.sqrt` on a physical tensor."""
    data = abs(ndarrays.r)
    old = physical.tensor(data, unit='m')
    new = numpy.sqrt(old)
    assert isinstance(new, physical.Tensor)
    assert numpy.array_equal(new, numpy.sqrt(data))
    assert new.unit == f"{old.unit}^1/2"


def test_squeeze(ndarrays: support.NDArrays):
    """Test `numpy.squeeze` on a physical tensor."""
    data = ndarrays.r[:, :1]
    old = physical.tensor(data, unit='m')
    new = numpy.squeeze(old)
    assert isinstance(new, physical.Tensor)
    assert numpy.array_equal(new, numpy.squeeze(data))
    assert new.unit == old.unit
    singular = physical.tensor([[2.0]], unit='m')
    scalar = numpy.squeeze(singular)
    assert isinstance(scalar, physical.Scalar)
    assert scalar.unit == singular.unit


def test_axis_mean():
    """Test `numpy.mean` along an axis of a physical tensor."""
    data = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    unit = 'm'
    old = physical.tensor(data, unit=unit)
    for axis in range(data.ndim):
        for a in (axis, axis-old.ndim):
            new = numpy.mean(old, axis=a)
            assert isinstance(new, physical.Tensor)
            assert numpy.array_equal(new, numpy.mean(data, axis=a))
            assert new.unit == old.unit


def test_full_mean():
    """Test `numpy.mean` of a full physical tensor."""
    data = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    old = physical.tensor(data, unit='m')
    new = numpy.mean(old)
    assert isinstance(new, physical.Scalar)
    assert numpy.array_equal(new.data, numpy.mean(data))
    assert new.unit == old.unit


def test_axis_sum():
    """Test `numpy.sum` along an axis of a physical tensor."""
    data = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    unit = 'm'
    old = physical.tensor(data, unit=unit)
    for axis in range(data.ndim):
        for a in (axis, axis-old.ndim):
            new = numpy.sum(old, axis=a)
            assert isinstance(new, physical.Tensor)
            assert numpy.array_equal(new, numpy.sum(data, axis=a))


def test_full_sum():
    """Test `numpy.sum` of a full physical tensor."""
    data = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    old = physical.tensor(data, unit='m')
    new = numpy.sum(old)
    assert isinstance(new, physical.Scalar)
    assert numpy.array_equal(new.data, numpy.sum(data))
    assert new.unit == old.unit


def test_axis_cumsum():
    """Test `numpy.cumsum` along an axis of a physical tensor."""
    data = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    unit = 'm'
    old = physical.tensor(data, unit=unit)
    for axis in range(data.ndim):
        for a in (axis, axis-old.ndim):
            new = numpy.cumsum(old, axis=a)
            assert isinstance(new, physical.Tensor)
            assert numpy.array_equal(new, numpy.cumsum(data, axis=a))
            assert new.unit == old.unit


def test_full_cumsum():
    """Test `numpy.cumsum` of a full physical tensor."""
    data = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    old = physical.tensor(data, unit='m')
    new = numpy.cumsum(old)
    assert isinstance(new, physical.Vector)
    assert numpy.array_equal(new.data, numpy.cumsum(data))
    assert new.unit == old.unit


def test_transpose():
    """Test `numpy.transpose` on a physical tensor."""
    data = numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    old = physical.tensor(data, unit='cm')
    test = [
        (0, 1, 2),
        (0, 2, 1),
        (1, 2, 0),
        (1, 0, 2),
        (2, 0, 1),
        (2, 1, 0),
        None,
    ]
    for axes in test:
        new = numpy.transpose(old, axes=axes)
        assert isinstance(new, physical.Tensor)
        assert numpy.array_equal(new.data, numpy.transpose(data, axes=axes))
        assert new.unit == old.unit


def test_gradient(ndarrays: support.NDArrays):
    """Test `numpy.gradient` on a physical tensor."""
    data = ndarrays.r
    tensor = physical.tensor(data, unit='m')
    cases = [
        {
            'dt': [],
            'unit': tensor.unit,
            'reference': numpy.gradient(data),
        },
        {
            'dt': [0.5],
            'unit': tensor.unit,
            'reference': numpy.gradient(data, 0.5),
        },
        {
            'dt': [physical.scalar(0.5, unit='s')],
            'unit': tensor.unit / 's',
            'reference': numpy.gradient(data, 0.5),
        },
        {
            'dt': [physical.tensor([0.5, 1.0, 1.5], unit='s')],
            'axis': 0,
            'unit': tensor.unit / 's',
            'reference': [numpy.gradient(data, [0.5, 1.0, 1.5], axis=0)],
        },
    ]
    for case in cases:
        dt = case.get('dt', [])
        gradient = numpy.gradient(tensor, *dt, axis=case.get('axis'))
        computed = gradient if isinstance(gradient, list) else [gradient]
        reference = case['reference']
        expected = reference if isinstance(reference, list) else [reference]
        unit = case['unit']
        for this, that in zip(computed, expected):
            assert isinstance(this, physical.Tensor)
            assert numpy.array_equal(this, that)
            assert this.unit == unit


def test_unit():
    """Test the ability to update a physical tensor's unit."""
    old = physical.tensor([2.0, 4.0], 'm')
    new = old.withunit('km')
    assert isinstance(new, type(old))
    assert new is not old
    assert new.unit == 'km'
    factor = old.unit >> new.unit
    assert numpy.array_equal(new, factor*numpy.array(old))
    with pytest.raises(ValueError):
        old.withunit('J')


