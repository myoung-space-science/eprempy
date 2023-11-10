import numbers
import operator as standard
import typing

import numpy
import numpy.typing
import pytest

import support
from eprempy import numeric
from eprempy import real


def test_factory(ndarrays: support.NDArrays):
    """Test various ways to create an array."""
    ndarray = ndarrays.r
    # Create an array with default dimensions.
    default = real.array(ndarray)
    assert isinstance(default, real.Array)
    assert numpy.array_equal(default.array, ndarray)
    assert default.dimensions == ('x0', 'x1')
    # Create arrays with named dimensions.
    dimensions = ('x', 'y')
    cases = (
        ((dimensions,), {}),
        (dimensions, {}),
        ((), {'dimensions': dimensions}),
    )
    for args, kwargs in cases:
        current = real.array(ndarray, *args, **kwargs)
        assert isinstance(current, real.Array)
        assert numpy.array_equal(current.array, ndarray)
        assert current.dimensions == dimensions
    # Check error cases.
    errors = (
        # number of named dimensions must match number of array dimensions
        (ndarray, dimensions[:-1], ValueError),
        # cannot change attributes on an existing instance
        (default, default.dimensions, TypeError),
    )
    for x, dimensions, error in errors:
        with pytest.raises(error):
            real.array(x, dimensions=dimensions)


def test_len():
    """Test the built-in `len(...)` function on an array.
    
    This test primarily exists to ensure that a data array is only as long as
    its numeric component.
    """
    values = [1.0, 2.0]
    this = real.array(values, dimensions=['x'])
    assert len(this) == len(values)
    that = real.array([values], dimensions=['x', 'y'])
    assert len(that) == len([values])


def test_equality():
    """Test equality-based comparative operations on arrays."""
    # a reference array
    ar = real.array([[1.0], [10.0], [5.0]], dimensions=['d0', 'd1'])
    # equal to the reference array
    br = real.array([[1.0], [10.0], [5.0]], dimensions=['d0', 'd1'])
    # equal values; different dimensions
    cr = real.array([[1.0], [10.0], [5.0]], dimensions=['d0', 'd2'])
    # equal dimenions; different values
    ax = real.array([[5.0], [10.0], [1.0]], dimensions=['d0', 'd1'])
    # different values; different dimensions
    ay = real.array([[5.0], [10.0], [1.0]], dimensions=['d0', 'd2'])
    # equal values; different shape
    az = real.array([1.0, 10.0, 5.0], dimensions=['d0'])
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
    dx = ['d0', 'd1']
    dy = ['d0', 'd2']
    dz = dx[0]
    # reference array
    xx = real.array(vx, dimensions=dx)
    # same dimensions
    yx = real.array(vy, dimensions=dx)
    valid = [
        (standard.lt, xx, yx),
        (standard.le, xx, yx),
        (standard.gt, xx, yx),
        (standard.ge, xx, yx),
    ]
    for f, a, b in valid:
        r = f(a._object, b._object)
        assert numpy.array_equal(f(a, b), r)
    # different dimensions
    yy = real.array(vy, dimensions=dy)
    # inconsistent shape
    zz = real.array(vz, dimensions=dz)
    invalid = [
        (standard.lt, xx, yy),
        (standard.le, xx, yy),
        (standard.gt, xx, yy),
        (standard.ge, xx, yy),
        (standard.lt, xx, zz),
        (standard.le, xx, zz),
        (standard.gt, xx, zz),
        (standard.ge, xx, zz),
    ]
    for f, a, b in invalid:
        with pytest.raises(ValueError):
            f(a, b)


def test_unary(ndarrays: support.NDArrays):
    """Test unary numerical operations on arrays."""
    this = real.array(ndarrays.r, dimensions=['x', 'y'])
    operators = [
        abs,
        standard.pos,
        standard.neg,
    ]
    for f in operators:
        ndarrays = f(this._object)
        expected = real.array(
            ndarrays,
            dimensions=this.dimensions,
        )
        assert f(this) == expected


def test_additive(ndarrays: support.NDArrays) -> None:
    """Test additive operations on arrays."""
    original = real.array(ndarrays.r, dimensions=['x', 'y'])
    samedims = real.array(ndarrays.xy, dimensions=['x', 'y'])
    valid = [
        # can add and subtract arrays with the same dimensions
        (original, samedims, real.Array),
        # can add and subtract a number
        (2.0, original.array, numpy.ndarray),
        # can add and subtract a numpy array
        (original, original.array, numpy.ndarray),
    ]
    operators = (standard.add, standard.sub)
    for f in operators:
        for a, b, t in valid:
            check_additive(f, a, b, t)
            check_additive(f, b, a, t)
    sharedim = real.array(ndarrays.yz, dimensions=['y', 'z'])
    diffdims = real.array(ndarrays.zw, dimensions=['z', 'w'])
    invalid = [
        # cannot add or subtract arrays with different dimensions
        (sharedim, original),
        (diffdims, original),
    ]
    for f in operators:
        for a, b in invalid:
            with pytest.raises(ValueError):
                f(a, b)
            with pytest.raises(ValueError):
                f(b, a)


def check_additive(
    f: typing.Callable,
    a: real.Array,
    b: real.Array,
    t: type,
) -> None:
    """Helper for `test_additive`."""
    new = f(a, b)
    assert isinstance(new, t)
    if isinstance(new, real.Array):
        expected = compute_data(f, a, b)
        assert numpy.array_equal(new, expected)
        assert new.dimensions == a.dimensions


def test_multiplicative(ndarrays: support.NDArrays) -> None:
    """Test multiplicative operations on arrays."""
    original = real.array(ndarrays.r, dimensions=['x', 'y'])
    samedims = real.array(ndarrays.xy, dimensions=['x', 'y'])
    sharedim = real.array(ndarrays.yz, dimensions=['y', 'z'])
    diffdims = real.array(ndarrays.zw, dimensions=['z', 'w'])
    extradim = real.array(ndarrays.xyz, dimensions=['x', 'y', 'z'])
    value = 2.0
    singular = real.array(
        [[value]],
        dimensions=original.dimensions,
    )
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
        (original, singular),
        (original, value),
        (original, numpy.array([value])),
        (singular, singular),
    ]
    for f in (standard.mul, standard.truediv):
        for a, b in operands:
            check_multiplicative(f, a, b)
            check_multiplicative(f, b, a)


def check_multiplicative(
    f: typing.Callable,
    a: typing.Union[real.Array, numbers.Real],
    b: typing.Union[real.Array, numbers.Real],
) -> None:
    """Helper for `test_multiplicative`."""
    new = f(a, b)
    assert isinstance(new, real.Array)
    expected = compute_data(f, a, b)
    assert numpy.array_equal(new, expected)
    if not isinstance(a, real.Array):
        assert new.dimensions == b.dimensions
    elif not isinstance(b, real.Array):
        assert new.dimensions == a.dimensions
    else:
        assert new.dimensions == a.dimensions | b.dimensions


def test_pow(ndarrays: support.NDArrays) -> None:
    """Test exponentiation on an array."""
    p = 3
    original = real.array(ndarrays.r, dimensions=['x', 'y'])
    samedims = real.array(ndarrays.xy, dimensions=['x', 'y'])
    valid = [
        # can raise an array by a number
        (original, p, real.Array),
        # can raise an array by an array with the same dimensions
        (original, samedims, real.Array),
        # can raise a number by an array
        (p, original, numpy.ndarray),
        # can raise a numpy array by an array
        (original.array, original, numpy.ndarray),
    ]
    for a, b, t in valid:
        check_pow(standard.pow, a, b, t)
    sharedim = real.array(ndarrays.yz, dimensions=['y', 'z'])
    diffdims = real.array(ndarrays.zw, dimensions=['z', 'w'])
    extradim = real.array(ndarrays.xyz, dimensions=['x', 'y', 'z'])
    invalid = [
        # cannot raise an array by any array
        (original, sharedim, ValueError),
        (sharedim, original, ValueError),
        (original, diffdims, ValueError),
        (diffdims, original, ValueError),
        (original, extradim, ValueError),
        (extradim, original, ValueError),
    ]
    for a, b, error in invalid:
        with pytest.raises(error):
            a ** b


def check_pow(
    f: typing.Callable,
    a: typing.Union[real.Array, numbers.Real],
    b: typing.Union[real.Array, numbers.Real],
    t: typing.Type,
) -> None:
    """Helper for `test_pow`."""
    new = f(a, b)
    assert isinstance(new, t)
    if isinstance(new, real.Array):
        expected = compute_data(f, a, b)
        assert numpy.array_equal(new, expected)
        if isinstance(a, real.Array):
            assert new.dimensions == a.dimensions


def compute_data(
    f: typing.Callable,
    a: typing.Union[real.Array, typing.SupportsFloat],
    b: typing.Union[real.Array, typing.SupportsFloat],
) -> numpy.ndarray:
    """Apply `f` to numerical attributes of `a` and `b`."""
    if all(not isinstance(i, real.Array) for i in (a, b)):
        raise TypeError("Expected at least one of a or b to be an array")
    if isinstance(b, typing.SupportsFloat):
        try:
            y = float(b[0])
        except (IndexError, TypeError):
            y = float(b)
        return f(a.array, y)
    if isinstance(a, typing.SupportsFloat):
        try:
            x = float(a[0])
        except (IndexError, TypeError):
            x = float(a)
        return f(x, b.array)
    return f(*real.Array.remesh(a, b))


def test_subscription(ndarrays: support.NDArrays) -> None:
    """Test various ways to subscript the array-like data container."""
    ndarray = ndarrays.r
    dimensions = ['x', 'y']
    this = real.array(ndarray, dimensions=dimensions)
    assert this.shape == ndarray.shape
    assert this.ndim == ndarray.ndim
    for sliced in (this[:], this[...]):
        assert isinstance(sliced, type(this))
        assert sliced is not this
        assert numpy.array_equal(sliced, ndarray)
    indices = [
        # same as x[0, :]
        (0, slice(None)),
        # same as x[:, 0]
        (slice(None), 0),
        # same as x[:, 0:1]
        (slice(None), slice(0, 1)),
        # same as x[(0, 1), :]
        ((0, 1), slice(None)),
        # same as x[:, (0, 1)]
        (slice(None), (0, 1)),
        # same as x[:, None, 0]
        (slice(None), None, 0),
        # same as x[None, :, 0]
        (None, slice(None), 0),
        # same as x[:2, 0]
        (slice(None, 2), 0),
        # same as x[1:, 0]
        (slice(1, None), 0),
    ]
    for index in indices:
        x = this[index]
        y = numpy.array(ndarray[index], ndmin=this.ndim).reshape(x.shape)
        assert numpy.array_equal(x, y)
        assert x.dimensions == numeric.dimensions(dimensions)
    # Providing an explicit point index produces a new array. This behavior
    # differs from that of a numpy array, in order to support
    # observation-related code.
    singular = real.array(
        numpy.array(ndarray[0, 0], ndmin=this.ndim),
        dimensions=this.dimensions,
    )
    assert this[0, 0] == singular
    assert this[(0, 0)] == singular
    # Subscripting a singular array with an explicit index produces a new array.
    # This is also inconsistent with numpy array behavior.
    point = real.array([1])
    assert isinstance(point[0], real.Array)
    # Subscripting a singular array with a slice, ellipsis, or range produces a
    # new array. This is consistent with numpy array behavior.
    assert isinstance(point[:], real.Array)
    assert isinstance(point[...], real.Array)
    assert isinstance(point[range(0, 1)], real.Array)
    # Boolean indices behave equivalently to the numpy case.
    expected = real.array(
        numpy.array(ndarray[ndarray < 0], ndmin=this.ndim),
        dimensions=this.dimensions,
    )
    assert this[this < 0] == expected


def test_squeeze(ndarrays: support.NDArrays):
    """Test `numpy.squeeze` on an array."""
    ndarray = ndarrays.r[:, :1]
    dimensions = ['x', 'y']
    old = real.array(ndarray, dimensions=dimensions)
    new = numpy.squeeze(old)
    assert isinstance(new, real.Array)
    assert numpy.array_equal(new, numpy.squeeze(ndarray))
    assert new.dimensions == numeric.dimensions(dimensions[0])
    singular = real.array([[2.0]], dimensions=dimensions)
    assert numpy.squeeze(singular) == 2.0


def test_axis_mean():
    """Test `numpy.mean` along an axis of an array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    old = real.array(ndarray, dimensions=['x', 'y', 'z'])
    cases = [
        ('y', 'z'),
        ('x', 'z'),
        ('x', 'y'),
    ]
    for axis, dimensions in enumerate(cases):
        for a in (axis, axis-old.ndim):
            new = numpy.mean(old, axis=a)
            assert isinstance(new, real.Array)
            assert numpy.array_equal(new, numpy.mean(ndarray, axis=a))
            assert new.dimensions == numeric.dimensions(dimensions)


def test_full_mean():
    """Test `numpy.mean` of a full physical array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    old = real.array(ndarray, dimensions=['x', 'y', 'z'])
    assert numpy.mean(old) == numpy.mean(ndarray)


def test_axis_sum():
    """Test `numpy.sum` along an axis of an array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    old = real.array(ndarray, dimensions=['x', 'y', 'z'])
    test = {
         0: ('y', 'z'),
         1: ('x', 'z'),
         2: ('x', 'y'),
        -1: ('x', 'y'),
    }
    for axis, dimensions in test.items():
        new = numpy.sum(old, axis=axis)
        assert isinstance(new, real.Array)
        assert numpy.array_equal(new, numpy.sum(ndarray, axis=axis))
        assert new.dimensions == numeric.dimensions(dimensions)


def test_full_sum():
    """Test `numpy.sum` of a full physical array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    old = real.array(ndarray, dimensions=['x', 'y', 'z'])
    assert numpy.sum(old) == numpy.sum(ndarray)


def test_axis_cumsum():
    """Test `numpy.cumsum` along an axis of an array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    dimensions = ['x', 'y', 'z']
    old = real.array(ndarray, dimensions=dimensions)
    for axis in (0, 1, 2, -1):
        new = numpy.cumsum(old, axis=axis)
        assert isinstance(new, real.Array)
        assert numpy.array_equal(new, numpy.cumsum(ndarray, axis=axis))
        assert new.dimensions == numeric.dimensions(dimensions)


def test_full_cumsum():
    """Test `numpy.cumsum` of a full physical array."""
    ndarray = 1 + numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    old = real.array(ndarray, dimensions=['x', 'y', 'z'])
    new = numpy.cumsum(old)
    assert isinstance(new, numpy.ndarray)
    assert numpy.array_equal(new, numpy.cumsum(ndarray))


def test_transpose():
    """Test `numpy.transpose` on an array."""
    ndarray = numpy.arange(3 * 4 * 5).reshape(3, 4, 5)
    dimensions = ['x', 'y', 'z']
    old = real.array(ndarray, dimensions=dimensions)
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
        assert isinstance(new, real.Array)
        assert numpy.array_equal(new, numpy.transpose(ndarray))
        assert new.dimensions == numeric.dimensions(dimensions)


def test_gradient(ndarrays: support.NDArrays):
    """Test `numpy.gradient` on an array."""
    ndarray = ndarrays.r
    dimensions = ['x', 'y']
    array = real.array(ndarray, dimensions=dimensions)
    cases = [
        {
            'dt': [],
            'reference': numpy.gradient(ndarray),
        },
        {
            'dt': [0.5],
            'reference': numpy.gradient(ndarray, 0.5),
        },
        {
            'dt': [numpy.array([0.5, 1.0, 1.5])],
            'axis': 0,
            'reference': [numpy.gradient(ndarray, [0.5, 1.0, 1.5], axis=0)],
        },
        {
            'dt': [real.array([0.5, 1.0, 1.5])],
            'axis': 0,
            'reference': [numpy.gradient(ndarray, [0.5, 1.0, 1.5], axis=0)],
        },
    ]
    for case in cases:
        dt = case.get('dt', [])
        gradient = numpy.gradient(array, *dt, axis=case.get('axis'))
        computed = gradient if isinstance(gradient, list) else [gradient]
        reference = case['reference']
        expected = reference if isinstance(reference, list) else [reference]
        for this, that in zip(computed, expected):
            assert isinstance(this, real.Array)
            assert numpy.array_equal(this, that)
            assert this.dimensions == numeric.dimensions(dimensions)


