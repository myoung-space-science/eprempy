import itertools
import numbers
import operator as standard
import typing

import numpy
import numpy.typing
import pytest

import support
from eprempy import measured
from eprempy import metric
from eprempy import numeric
from eprempy import physical
from eprempy import real


def test_factory(ndarrays: support.NDArrays) -> None:
    """Test various ways to create a physical array."""
    ndarray = ndarrays.r
    unit = 'm'
    dimensions = ('x', 'y')
    axes = {d: numpy.arange(i) for (d, i) in zip(dimensions, ndarray.shape)}
    axes = physical.axes(axes)
    default = {'unit': '1', 'axes': physical.axes(*ndarray.shape)}
    defined = {'unit': unit, 'axes': axes}
    cases = (
        # create an array with default attributes
        ({}, default),
        # create an array with default axes
        ({'unit': unit}, {'unit': defined['unit'], 'axes': default['axes']}),
        # create an array with default unit
        ({'axes': axes}, {'unit': default['unit'], 'axes': defined['axes']}),
        # create an array from data, unit, and various forms of axes
        ({'unit': unit, 'axes': axes}, defined),
        ({'unit': unit, 'axes': axes}, defined),
        ({'unit': unit, 'axes': axes.dimensions}, defined),
        ({'unit': unit, 'axes': tuple(axes.dimensions)}, defined),
    )
    for kwargs, expected in cases:
        current = physical.array(ndarray, **kwargs)
        assert isinstance(current.data, real.Array)
        assert current.unit == expected['unit']
        assert current.axes == expected['axes']
    # Create an array from existing instance.
    this = physical.array(ndarray, unit=unit, axes=axes)
    that = physical.array(this)
    assert isinstance(that.data, real.Array)
    assert that.unit == unit
    assert this.axes == axes
    # Check error cases
    with pytest.raises(ValueError):
        physical.array(physical.tensor(ndarray), unit=unit)
    with pytest.raises(ValueError):
        physical.array(this, unit=unit)
    with pytest.raises(ValueError):
        physical.array(this, axes=axes)
    with pytest.raises(ValueError):
        physical.array(this, unit=unit, axes=axes)
    with pytest.raises(ValueError):
        physical.array(this, unit=unit, axes=dimensions)


def test_equality():
    """Test equality-based comparative operations on arrays."""
    # a reference array
    ar = physical.array([[1.0], [10.0], [5.0]], axes=['d0', 'd1'])
    # equal to the reference array
    br = physical.array([[1.0], [10.0], [5.0]], axes=['d0', 'd1'])
    # equal values; different dimensions
    cr = physical.array([[1.0], [10.0], [5.0]], axes=['d0', 'd2'])
    # equal dimenions; different values
    ax = physical.array([[5.0], [10.0], [1.0]], axes=['d0', 'd1'])
    # different values; different dimensions
    ay = physical.array([[5.0], [10.0], [1.0]], axes=['d0', 'd2'])
    # equal values; different shape
    az = physical.array([1.0, 10.0, 5.0], axes=['d0'])
    # directly test "equal" via __eq__
    assert ar == br
    for other in (cr, ax, ay, az):
        # directly test "not equal" via __ne__
        assert ar != other
        # indirectly test "not equal" via __eq__
        assert not (ar == other)


def test_ordering():
    """Test ordering-based comparative operations on arrays."""
    vx = numpy.array([[1.0], [10.0], [5.0]])
    vy = numpy.array([[5.0], [10.0], [1.0]])
    vz = vx[:, 0]
    ux = 'm / s'
    uy = 'J'
    dx = ['d0', 'd1']
    dy = ['d0', 'd2']
    dz = dx[:-1]
    # reference array
    xxx = physical.array(vx, unit=ux, axes=dx)
    # same unit; same dimensions
    yxx = physical.array(vy, unit=ux, axes=dx)
    valid = [
        (standard.lt, xxx, yxx),
        (standard.le, xxx, yxx),
        (standard.gt, xxx, yxx),
        (standard.ge, xxx, yxx),
    ]
    for f, a, b in valid:
        r = f(a.data, b.data)
        assert numpy.array_equal(f(a, b), physical.array(r))
    # same unit; different dimensions
    yxy = physical.array(vy, unit=ux, axes=dy)
    # different unit; same dimensions
    yyx = physical.array(vy, unit=uy, axes=dx)
    # same unit; inconsistent shape
    zxz = physical.array(vz, unit=ux, axes=dz)
    invalid = [
        (standard.lt, xxx, yxy),
        (standard.le, xxx, yxy),
        (standard.gt, xxx, yxy),
        (standard.ge, xxx, yxy),
        (standard.lt, xxx, yyx),
        (standard.le, xxx, yyx),
        (standard.gt, xxx, yyx),
        (standard.ge, xxx, yyx),
        (standard.lt, xxx, zxz),
        (standard.le, xxx, zxz),
        (standard.gt, xxx, zxz),
        (standard.ge, xxx, zxz),
    ]
    for f, a, b in invalid:
        with pytest.raises(ValueError):
            f(a, b)


def test_cast(ndarrays: support.NDArrays):
    """Test casting operations on arrays."""
    ndarray = ndarrays.r
    metadata = {
        'unit': 'm',
        'axes': ['x', 'y'],
    }
    array = physical.array(ndarray, **metadata)
    operators = [
        int,
        float,
        complex,
    ]
    for f in operators:
        assert f(array[1, 1]) == f(array.data.array[1, 1])
        with pytest.raises(TypeError):
            f(array)


def test_unary(ndarrays: support.NDArrays):
    """Test unary numerical operations on arrays."""
    ndarray = ndarrays.r
    metadata = {
        'unit': 'm',
        'axes': ['x', 'y'],
    }
    array = physical.array(ndarray, **metadata)
    operators = [
        abs,
        standard.pos,
        standard.neg,
    ]
    for f in operators:
        assert f(array) == physical.array(f(ndarray), **metadata)


def test_additive(ndarrays: support.NDArrays) -> None:
    """Test additive operations on physical arrays."""
    dxy = ['x', 'y']
    dyz = ['y', 'z']
    dzw = ['z', 'w']
    meter = 'm'
    joule = 'J'
    original = physical.array(ndarrays.r, unit=meter, axes=dxy)
    samedims = physical.array(ndarrays.xy, unit=meter, axes=dxy)
    valid = [
        # same unit; same dimensions
        (original, samedims),
    ]
    operators = (standard.add, standard.sub)
    for f in operators:
        for a, b in valid:
            check_additive(f, a, b)
            check_additive(f, b, a)
    sharedim = physical.array(ndarrays.yz, unit=meter, axes=dyz)
    diffdims = physical.array(ndarrays.zw, unit=meter, axes=dzw)
    diffunit = physical.array(ndarrays.r, unit=joule, axes=dxy)
    invalid = [
        # can't add or subtract arrays with different dimensions
        (sharedim, original),
        (diffdims, original),
        # can't add or subtract arrays with different units
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
    a: physical.Array,
    b: physical.Array,
) -> None:
    """Helper for `test_additive`."""
    new = f(a, b)
    assert isinstance(new, physical.Array)
    expected = compute(f, a, b)
    assert numpy.array_equal(new, expected)
    assert new.unit == a.unit
    assert new.axes == a.axes


def test_additive_broadcast(ndarrays: support.NDArrays) -> None:
    """Test additive operations with broadcasting on physical arrays."""
    axes = ['x', 'y']
    unit = 'm'
    original = physical.array(ndarrays.r, unit=unit, axes=axes)
    a = original[:]
    b = original[0, :]
    r = a - b
    assert isinstance(r, physical.Array)
    assert numpy.array_equal(r, a.data.array - b.data.array)
    assert r.unit == a.unit
    assert r.axes == a.axes
    with pytest.raises(ValueError): # numpy-level broadcasting error
        original[:] - original[:2, 0]


def test_multiplicative(ndarrays: support.NDArrays) -> None:
    """Test multiplicative operations on physical arrays."""
    dxy = ['x', 'y']
    dyz = ['y', 'z']
    dzw = ['z', 'w']
    dxyz = ['x', 'y', 'z']
    meter = 'm'
    joule = 'J'
    original = physical.array(ndarrays.r, unit=meter, axes=dxy)
    samedims = physical.array(ndarrays.xy, unit=meter, axes=dxy)
    sharedim = physical.array(ndarrays.yz, unit=meter, axes=dyz)
    diffdims = physical.array(ndarrays.zw, unit=meter, axes=dzw)
    diffunit = physical.array(ndarrays.r, unit=joule, axes=dxy)
    extradim = physical.array(ndarrays.xyz, unit=meter, axes=dxyz)
    value = 2.0
    singular = physical.array([[value]], unit=meter, axes=dxy)
    operands = [
        (original, samedims),
        (original, sharedim),
        (original, extradim),
        (original, diffdims),
        (samedims, sharedim),
        (samedims, extradim),
        (samedims, diffdims),
        (extradim, sharedim),
        (extradim, diffdims),
        (diffdims, sharedim),
        (original, diffunit),
        (original, singular),
        (original, value),
        (singular, singular),
    ]
    for f in (standard.mul, standard.truediv):
        for a, b in operands:
            check_multiplicative(f, a, b)
            check_multiplicative(f, b, a)


def check_multiplicative(
    f: typing.Callable,
    a: typing.Union[physical.Array, numbers.Real],
    b: typing.Union[physical.Array, numbers.Real],
) -> None:
    """Helper for `test_multiplicative`."""
    new = f(a, b)
    assert isinstance(new, physical.Array)
    expected = compute(f, a, b)
    assert numpy.array_equal(new, expected)
    if isinstance(a, numbers.Real):
        unit = f('1', b.unit)
        axes = b.axes
    elif isinstance(b, numbers.Real):
        unit = a.unit
        axes = a.axes
    else:
        unit = f(a.unit, b.unit)
        axes = a.axes | b.axes
    assert new.unit == unit
    assert new.axes == axes


def test_pow(ndarrays: support.NDArrays) -> None:
    """Test exponentiation on a physical array."""
    dxy = ['x', 'y']
    dyz = ['y', 'z']
    dzw = ['z', 'w']
    dxyz = ['x', 'y', 'z']
    meter = 'm'
    joule = 'J'
    original = physical.array(ndarrays.r, unit=meter, axes=dxy)
    p = 3
    unitless = physical.array(ndarrays.r, axes=dxy)
    valid = [
        # can raise a array by a number
        (original, p, physical.Array),
        # can raise a unitless array by a unitless array
        (unitless, unitless, physical.Array),
        # can raise a number by a unitless array
        (p, unitless, numpy.ndarray),
        # can raise a numpy array by a unitless array
        (numpy.array(original.data), unitless, numpy.ndarray)
    ]
    for a, b, t in valid:
        check_pow(standard.pow, a, b, t)
    samedims = physical.array(ndarrays.xy, unit=meter, axes=dxy)
    sharedim = physical.array(ndarrays.yz, unit=meter, axes=dyz)
    diffdims = physical.array(ndarrays.zw, unit=meter, axes=dzw)
    diffunit = physical.array(ndarrays.r, unit=joule, axes=dxy)
    extradim = physical.array(ndarrays.xyz, unit=meter, axes=dxyz)
    invalid = [
        # a non-numeric exponent is meaningless
        (original, '1', TypeError),
        # cannot raise a unitful array by even a unitless array
        (original, unitless, ValueError),
        # cannot raise anything by a unitful array
        (p, original, ValueError),
        (numpy.array(original.data), original, ValueError),
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
    a: typing.Union[physical.Array, numbers.Real],
    b: typing.Union[physical.Array, numbers.Real],
    t: typing.Type[measured.ObjectT]=physical.Array,
) -> None:
    """Helper for `test_pow`."""
    new = f(a, b)
    assert isinstance(new, t)
    if isinstance(new, physical.Array):
        expected = compute(f, a, b)
        assert numpy.array_equal(new, expected)
        assert new.axes == a.axes
        if a.isunitless:
            assert new.unit == '1'
        else:
            p = b.data if isinstance(b, physical.Object) else b
            assert new.unit == f(a.unit, p)


def compute(
    f: typing.Callable,
    a: typing.Union[physical.Array, numbers.Real],
    b: typing.Union[physical.Array, numbers.Real],
) -> numpy.ndarray:
    """Compute the result of `f(a, b)`."""
    if all(not isinstance(i, physical.Array) for i in (a, b)):
        raise TypeError("Expected at least one of a or b to be an array")
    if isinstance(b, numbers.Real):
        return f(a.data, float(b))
    if isinstance(a, numbers.Real):
        return f(float(a), b.data)
    return f(*numeric.remesh(a.data, b.data))


def test_trig(ndarrays: support.NDArrays):
    """Test `numpy` trigonometric ufuncs on a physical array."""
    dimensions = ['x', 'y']
    for f in (numpy.sin, numpy.cos, numpy.tan):
        for unit in {'rad', 'deg'}:
            old = physical.array(
                ndarrays.r,
                unit=unit,
                axes=dimensions,
            )
            new = f(old)
            assert isinstance(new, physical.Array)
            assert numpy.array_equal(new, f(old.data))
            assert new.unit == '1'
        bad = physical.array(
            ndarrays.r,
            unit='m',
            axes=dimensions,
        )
        with pytest.raises(ValueError):
            f(bad)


def test_sqrt(ndarrays: support.NDArrays):
    """Test `numpy.sqrt` on a physical array."""
    ndarray = abs(ndarrays.r)
    dimensions = ['x', 'y']
    old = physical.array(
        ndarray,
        unit='m',
        axes=dimensions,
    )
    new = numpy.sqrt(old)
    assert isinstance(new, physical.Array)
    assert numpy.array_equal(new, numpy.sqrt(ndarray))
    assert new.dimensions == numeric.dimensions(dimensions)
    assert new.unit == f"{old.unit}^1/2"


def test_squeeze(ndarrays: support.NDArrays):
    """Test `numpy.squeeze` on a physical array."""
    ndarray = ndarrays.r[:, :1]
    unit = 'm'
    dimensions = ['x', 'y']
    old = physical.array(
        ndarray,
        unit=unit,
        axes=dimensions,
    )
    new = numpy.squeeze(old)
    assert isinstance(new, physical.Array)
    assert numpy.array_equal(new, numpy.squeeze(ndarray))
    assert new.dimensions == numeric.dimensions(dimensions[0])
    assert new.unit == metric.unit(unit)
    singular = physical.array(
        [[2.0]],
        unit=unit,
        axes=dimensions,
    )
    scalar = numpy.squeeze(singular)
    assert isinstance(scalar, physical.Scalar)
    assert new.unit == metric.unit(unit)


def test_axis_mean():
    """Test `numpy.mean` along an axis of a physical array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    unit = 'm'
    old = physical.array(
        ndarray,
        unit=unit,
        axes=['x', 'y', 'z'],
    )
    cases = [
        ('y', 'z'),
        ('x', 'z'),
        ('x', 'y'),
    ]
    for axis, dimensions in enumerate(cases):
        for a in (axis, axis-old.ndim):
            new = numpy.mean(old, axis=a)
            assert isinstance(new, physical.Array)
            assert numpy.array_equal(new, numpy.mean(ndarray, axis=a))
            assert new.dimensions == numeric.dimensions(dimensions)
            assert new.unit == metric.unit(unit)


def test_full_mean():
    """Test `numpy.mean` of a full physical array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    unit = 'm'
    old = physical.array(
        ndarray,
        unit=unit,
        axes=['x', 'y', 'z'],
    )
    new = numpy.mean(old)
    assert isinstance(new, physical.Scalar)
    assert float(new) == numpy.mean(ndarray)
    assert new.unit == metric.unit(unit)


def test_axis_sum():
    """Test `numpy.sum` along an axis of a physical array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    unit = 'm'
    old = physical.array(
        ndarray,
        unit=unit,
        axes=['x', 'y', 'z'],
    )
    test = {
        0: ('y', 'z'),
        1: ('x', 'z'),
        2: ('x', 'y'),
        -1: ('x', 'y'),
    }
    for axis, dimensions in test.items():
        new = numpy.sum(old, axis=axis)
        assert isinstance(new, physical.Array)
        assert numpy.array_equal(new, numpy.sum(ndarray, axis=axis))
        assert new.dimensions == numeric.dimensions(dimensions)
        assert new.unit == metric.unit(unit)


def test_full_sum():
    """Test `numpy.sum` of a full physical array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    unit = 'm'
    old = physical.array(
        ndarray,
        unit=unit,
        axes=['x', 'y', 'z'],
    )
    new = numpy.sum(old)
    assert isinstance(new, physical.Scalar)
    assert float(new) == numpy.sum(ndarray)
    assert new.unit == metric.unit(unit)


def test_axis_cumsum():
    """Test `numpy.cumsum` along an axis of a physical array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    unit = 'm'
    dimensions = ['x', 'y', 'z']
    old = physical.array(
        ndarray,
        unit=unit,
        axes=dimensions,
    )
    for axis in (0, 1, 2, -1):
        new = numpy.cumsum(old, axis=axis)
        assert isinstance(new, physical.Array)
        assert numpy.array_equal(new, numpy.cumsum(ndarray, axis=axis))
        assert new.dimensions == numeric.dimensions(dimensions)
        assert new.unit == metric.unit(unit)


def test_full_cumsum():
    """Test `numpy.cumsum` of a full physical array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    unit = 'm'
    old = physical.array(
        ndarray,
        unit=unit,
        axes=['x', 'y', 'z'],
    )
    new = numpy.cumsum(old)
    assert isinstance(new, physical.Vector)
    assert numpy.array_equal(new, numpy.cumsum(ndarray))
    assert new.unit == metric.unit(unit)


def test_transpose():
    """Test `numpy.transpose` on a physical array."""
    ndarray = numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    unit = 'cm'
    dimensions = ['x', 'y', 'z']
    old = physical.array(ndarray, unit=unit, axes=dimensions)
    test = {
        (0, 1, 2): old.dimensions,
        (0, 2, 1): ['x', 'z', 'y'],
        (1, 2, 0): ['y', 'z', 'x'],
        (1, 0, 2): ['y', 'x', 'z'],
        (2, 0, 1): ['z', 'x', 'y'],
        (2, 1, 0): old.dimensions[::-1],
        None: old.dimensions[::-1],
    }
    for axes, dimensions in test.items():
        new = numpy.transpose(old, axes=axes)
        assert isinstance(new, physical.Array)
        assert numpy.array_equal(new, numpy.transpose(ndarray))
        assert new.unit == metric.unit(unit)
        assert new.dimensions == numeric.dimensions(dimensions)


def test_gradient(ndarrays: support.NDArrays):
    """Test `numpy.gradient` on a physical array."""
    ndarray = ndarrays.r
    dimensions = ['x', 'y']
    array = physical.array(ndarray, unit='m', axes=dimensions)
    cases = [
        {
            'dt': [],
            'unit': array.unit,
            'reference': numpy.gradient(ndarray),
        },
        {
            'dt': [0.5],
            'unit': array.unit,
            'reference': numpy.gradient(ndarray, 0.5),
        },
        {
            'dt': [physical.scalar(0.5, unit='s')],
            'unit': array.unit / 's',
            'reference': numpy.gradient(ndarray, 0.5),
        },
        {
            'dt': [physical.array([0.5, 1.0, 1.5], unit='s')],
            'axis': 0,
            'unit': array.unit / 's',
            'reference': [numpy.gradient(ndarray, [0.5, 1.0, 1.5], axis=0)],
        },
    ]
    for case in cases:
        dt = case.get('dt', [])
        gradient = numpy.gradient(array, *dt, axis=case.get('axis'))
        computed = gradient if isinstance(gradient, list) else [gradient]
        reference = case['reference']
        expected = reference if isinstance(reference, list) else [reference]
        unit = case['unit']
        for this, that in zip(computed, expected):
            assert isinstance(this, physical.Array)
            assert numpy.array_equal(this, that)
            assert this.unit == metric.unit(unit)
            assert this.dimensions == numeric.dimensions(dimensions)


def test_string_transpose(ndarrays: support.NDArrays):
    """Test the ability to transpose an array by dimensions."""
    ndarray = ndarrays.xyz
    dimensions = ['x', 'y', 'z']
    array = physical.array(ndarray, axes=dimensions)
    assert array.transpose() is array
    for permutation in itertools.permutations(dimensions):
        axes = [dimensions.index(d) for d in permutation]
        expected = ndarray.transpose(axes)
        byname = array.transpose(permutation)
        byaxis = array.transpose(axes)
        for x in (byname, byaxis):
            assert isinstance(x, physical.Array)
            assert x.dimensions == permutation
            assert numpy.array_equal(x, expected)
    with pytest.raises(ValueError):
        array.transpose('x', 'w', 'y', 'z')
    with pytest.raises(ValueError):
        array.transpose('x', 'z')


