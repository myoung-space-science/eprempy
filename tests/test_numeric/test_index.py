import numpy
import numpy.typing
import pytest

from eprempy import measured
from eprempy import numeric


@pytest.fixture
def index_args():
    """Arguments that can initialize an instance of `real.Index`."""
    return [
        # an integral number
        1,
        # an integral numeric string
        '1',
        # a 0-D array
        numpy.array(1, dtype=int),
        # a measured value
        measured.value(1),
        # a singular range
        range(1, 2),
        # a single-valued array-like object with integral value
        [1],
        (1,),
        numpy.array([1], dtype=int),
        measured.sequence(1),
    ]


def test_value_factory(index_args):
    """Test various ways to create an index value."""
    for arg in index_args:
        x = numeric.index.value(arg)
        assert int(x) == 1
    errors = [
        # numbers must be integral
        (1.0, TypeError),
        # numeric strings must be integral
        ('1.0', TypeError),
        # arrays must have integral type
        (numpy.array([1], dtype=float), TypeError),
        # for consistency with `Indices`
        ({1}, TypeError),
        # a dict is neither numeric nor array-like
        ({1: 'a'}, TypeError),
        # for consistency with `Indices`
        (slice(1, 2), TypeError),
        # an index must have a single value
        (numpy.array([1, 2], dtype=int), TypeError),
        (numpy.array([1, 2], dtype=float), TypeError),
        (measured.sequence([1, 2]), TypeError),
        # an index must be unitless
        (measured.value(1, unit='m'), ValueError),
        (measured.sequence(1, unit='m'), ValueError),
    ]
    for arg, error in errors:
        with pytest.raises(error):
            numeric.index.value(arg)


def test_value_operators():
    """Test numeric operations on an numeric.index."""
    unary = (
        (numeric.operators.abs,  3, numeric.index.value( 3)),
        (numeric.operators.abs, -3, numeric.index.value( 3)),
        (numeric.operators.pos,  3, numeric.index.value( 3)),
        (numeric.operators.pos, -3, numeric.index.value(-3)),
        (numeric.operators.neg,  3, numeric.index.value(-3)),
        (numeric.operators.neg, -3, numeric.index.value( 3)),
    )
    for f, a, r in unary:
        assert f(numeric.index.value(a)) == r
    binary = (
        (numeric.operators.eq,       3, 3, numpy.array([True])),
        (numeric.operators.ne,       3, 2, numpy.array([True])),
        (numeric.operators.lt,       3, 4, numpy.array([True])),
        (numeric.operators.gt,       3, 2, numpy.array([True])),
        (numeric.operators.le,       3, 4, numpy.array([True])),
        (numeric.operators.le,       3, 3, numpy.array([True])),
        (numeric.operators.ge,       3, 2, numpy.array([True])),
        (numeric.operators.ge,       3, 3, numpy.array([True])),
        (numeric.operators.add,      3, 3, numeric.index.value(6)),
        (numeric.operators.sub,      3, 3, numeric.index.value(0)),
        (numeric.operators.mul,      3, 3, numeric.index.value(9)),
        (numeric.operators.floordiv, 3, 3, numeric.index.value(1)),
        (numeric.operators.mod,      3, 3, numeric.index.value(0)),
        (numeric.operators.pow,      3, 2, numeric.index.value(9)),
    )
    for f, a, b, r in binary:
        assert f(a, numeric.index.value(b)) == r
        assert f(numeric.index.value(a), b) == r
        assert f(numeric.index.value(a), numeric.index.value(b)) == r
    errors = (
        (numeric.operators.truediv,  3,  3, TypeError),
        (numeric.operators.truediv, -3,  3, TypeError),
        (numeric.operators.truediv,  3, -3, TypeError),
        (numeric.operators.truediv, -3, -3, TypeError),
        (numeric.operators.pow,      3, -3, ValueError),
        (numeric.operators.pow,     -3, -3, ValueError),
    )
    for f, a, b, e in errors:
        with pytest.raises(e):
            f(a, numeric.index.value(b))
        with pytest.raises(e):
            f(numeric.index.value(a), b)
        with pytest.raises(e):
            f(numeric.index.value(a), numeric.index.value(b))


def test_sequence_factory(index_args):
    """Test various ways to create an index sequence."""
    # Anything that can initialize `Value` can initialize `Sequence`
    for arg in index_args:
        x = numeric.index.sequence(arg)
        assert list(x) == [1]
    valid = [
        # a non-singular range
        range(1, 3),
        # a sequence of numeric strings
        ['1', '2'],
        ('1', '2'),
        # a multi-valued array-like object
        [1, 2],
        (1, 2),
        numpy.array([1, 2], dtype=int),
        measured.sequence([1, 2]),
        # ... array may have dimension > 1 if it is logically 1-D
        numpy.array([1, 2], ndmin=2),
        numpy.array([1, 2], ndmin=3),
        numpy.array([[1], [2]]),
    ]
    for arg in valid:
        x = numeric.index.sequence(arg)
        assert list(x) == [1, 2]
    errors = [
        # numeric sequences must have only integral elements
        ([1.0, 2], TypeError),
        ((1.0, 2), TypeError),
        (['1.0', '2'], TypeError),
        (('1.0', '2'), TypeError),
        # arrays must have integral type
        (numpy.array([1, 2], dtype=float), TypeError),
        # set elements are unordered
        ({1, 2}, TypeError),
        # a dict is neither numeric nor array-like
        ({1: 'a', 2: 'b'}, TypeError),
        # a slice is not iterable
        (slice(1, 3), TypeError),
        # indices must be logically one-dimensional
        (numpy.array([[1, 2], [3, 4]]), TypeError),
        # indices must be unitless
        (measured.value(1, unit='m'), ValueError),
        (measured.sequence(1, unit='m'), ValueError),
        (measured.sequence([1, 2], unit='m'), ValueError),
    ]
    for arg, error in errors:
        with pytest.raises(error):
            numeric.index.sequence(arg)


def test_sequence_operators():
    """Test numeric operations on an indices."""
    unary = (
        (numeric.operators.abs,  3, numeric.index.sequence( 3)),
        (numeric.operators.abs, -3, numeric.index.sequence( 3)),
        (numeric.operators.pos,  3, numeric.index.sequence( 3)),
        (numeric.operators.pos, -3, numeric.index.sequence(-3)),
        (numeric.operators.neg,  3, numeric.index.sequence(-3)),
        (numeric.operators.neg, -3, numeric.index.sequence( 3)),
    )
    for f, a, r in unary:
        assert f(numeric.index.sequence(a)) == r
    binary = (
        (numeric.operators.eq,       3, 3, numpy.array([True])),
        (numeric.operators.ne,       3, 2, numpy.array([True])),
        (numeric.operators.lt,       3, 4, numpy.array([True])),
        (numeric.operators.gt,       3, 2, numpy.array([True])),
        (numeric.operators.le,       3, 4, numpy.array([True])),
        (numeric.operators.le,       3, 3, numpy.array([True])),
        (numeric.operators.ge,       3, 2, numpy.array([True])),
        (numeric.operators.ge,       3, 3, numpy.array([True])),
        (numeric.operators.add,      3, 3, numeric.index.sequence(6)),
        (numeric.operators.sub,      3, 3, numeric.index.sequence(0)),
        (numeric.operators.mul,      3, 3, numeric.index.sequence(9)),
        (numeric.operators.floordiv, 3, 3, numeric.index.sequence(1)),
        (numeric.operators.mod,      3, 3, numeric.index.sequence(0)),
        (numeric.operators.pow,      3, 2, numeric.index.sequence(9)),
    )
    for f, a, b, r in binary:
        assert f(a, numeric.index.sequence(b)) == r
        assert f(numeric.index.sequence(a), b) == r
        assert f(numeric.index.sequence(a), numeric.index.sequence(b)) == r
    errors = (
        (numeric.operators.truediv,  3,  3, TypeError),
        (numeric.operators.truediv, -3,  3, TypeError),
        (numeric.operators.truediv,  3, -3, TypeError),
        (numeric.operators.truediv, -3, -3, TypeError),
        (numeric.operators.pow,      3, -3, ValueError),
        (numeric.operators.pow,     -3, -3, ValueError),
    )
    for f, a, b, e in errors:
        with pytest.raises(e):
            f(a, numeric.index.sequence(b))
        with pytest.raises(e):
            f(numeric.index.sequence(a), b)
        with pytest.raises(e):
            f(numeric.index.sequence(a), numeric.index.sequence(b))


def test_sequence_subscription():
    """Test the behavior of indices when subscripted."""
    data = numpy.arange(10, dtype=int)
    original = numeric.index.sequence(data)
    sequence = original[1:4]
    assert isinstance(sequence, numeric.index.Sequence)
    assert numpy.array_equal(sequence.data, data[1:4])
    value = original[4]
    assert isinstance(value, numeric.index.Value)
    assert value.data == data[4]


def test_index_shift():
    """Test the linear-shift method on all index objects."""
    value = numeric.index.value(10)
    assert value.shift(+5) == numeric.index.value(15)
    assert value.shift(+5, ceil=14) == numeric.index.value(14)
    assert value.shift(+5, ceil=20) == numeric.index.value(15)
    assert value.shift(-5) == numeric.index.value(5)
    assert value.shift(-5, floor=6) == numeric.index.value(6)
    assert value.shift(-5, floor=0) == numeric.index.value(5)
    sequence = numeric.index.sequence([10, 11])
    assert all(sequence.shift(+5) == numeric.index.sequence([15, 16]))
    assert all(sequence.shift(+5, ceil=15) == numeric.index.sequence([15, 15]))
    assert all(sequence.shift(+5, ceil=20) == numeric.index.sequence([15, 16]))
    assert all(sequence.shift(-5) == numeric.index.sequence([5, 6]))
    assert all(sequence.shift(-5, floor=6) == numeric.index.sequence([6, 6]))
    assert all(sequence.shift(-5, floor=0) == numeric.index.sequence([5, 6]))


def test_normalize():
    """Test the function that computes array indices."""
    shape = (3, 4, 5)
    assert numeric.index.normalize(shape, ...) == ...
    assert numeric.index.normalize(shape, (...,)) == (...,)
    assert numeric.index.normalize(shape, slice(None)) == slice(None)
    assert numeric.index.normalize(shape, (slice(None),)) == (slice(None),)
    assert numeric.index.normalize(shape, (0, 1, 2)) == (0, 1, 2)
    assert numpy.array_equal(
        numeric.index.normalize(shape, numpy.array([0, 1, 2])),
        numpy.array([0, 1, 2]),
    )
    assert numpy.array_equal(
        numeric.index.normalize(shape, numpy.array([True, False, True])),
        numpy.array([True, False, True]),
    )
    result = numeric.index.normalize(
        shape,
        (slice(None), slice(None), (0, 1)),
    )
    expected = (
        numpy.array(range(3)).reshape(3, 1, 1),
        numpy.array(range(4)).reshape(1, 4, 1),
        numpy.array([0, 1]).reshape(1, 1, 2),
    )
    for x, y in zip(result, expected):
        assert numpy.array_equal(x, y)
    result = numeric.index.normalize(shape, (1, range(3), range(4)))
    expected = (
        numpy.array([1]).reshape(1, 1, 1),
        numpy.array(range(3)).reshape(1, 3, 1),
        numpy.array(range(4)).reshape(1, 1, 4),
    )
    for x, y in zip(result, expected):
        assert numpy.array_equal(x, y)


def test_expand():
    """Test the function that expands array indices."""
    cases = (
        (3, ...,          (slice(None), slice(None), slice(None))),
        (3, slice(None),  (slice(None), slice(None), slice(None))),
        (3, (..., -2, 4), (slice(None), -2, 4)),
        (4, (..., -2, 4), (slice(None), slice(None), -2, 4)),
        (3, (-2, ..., 4), (-2, slice(None), 4)),
        (4, (-2, ..., 4), (-2, slice(None), slice(None), 4)),
        (2, (-2, 4, ...), (-2, 4)),
        (3, (-2, 4, ...), (-2, 4, slice(None))),
        (4, (-2, 4, ...), (-2, 4, slice(None), slice(None))),
        (2, (-2, 4),      (-2, 4)),
        (3, (-2, 4),      (-2, 4)),
        (4, (-2, 4),      (-2, 4)),
        (1, 3,            (3,)),
        (2, 3,            (3, slice(None))),
        (3, 3,            (3, slice(None), slice(None))),
    )
    for ndim, arg, expected in cases:
        assert numeric.index.expand(ndim, arg) == expected
    errors = (
        (2, (..., -2, 4),     IndexError),
        (2, (-2, ..., 4),     IndexError),
        (4, (1, ..., 2, ...), IndexError),
    )
    for ndim, arg, error in errors:
        with pytest.raises(error):
            numeric.index.expand(ndim, arg)

