"""
Tests involving physical objects of mixed types.
"""

import operator as standard
import typing

import numpy
import numpy.typing
import pytest

from eprempy import physical


class Objects(typing.NamedTuple):
    """A collection of named physical objects for testing."""
    scalar: physical.Scalar
    vector: physical.Vector
    tensor: physical.Tensor
    array: physical.Array


@pytest.fixture
def value():
    """A single numeric value for test objects."""
    return 2.0


@pytest.fixture
def values():
    """Multiple numeric values for test objects."""
    return [2.0, 3.0]


@pytest.fixture
def unitless(value, values):
    """Unitless physical objects for testing."""
    unit = '1'
    return Objects(
        scalar=physical.scalar(value, unit=unit),
        vector=physical.vector(values, unit=unit),
        tensor=physical.tensor([values], unit=unit),
        array=physical.array([values], unit=unit, axes=('x', 'y'))
    )


@pytest.fixture
def unitful(value, values):
    """Unitful physical objects for testing."""
    unit = 'm'
    return Objects(
        scalar=physical.scalar(value, unit=unit),
        vector=physical.vector(values, unit=unit),
        tensor=physical.tensor([values], unit=unit),
        array=physical.array([values], unit=unit, axes=('x', 'y'))
    )


@pytest.mark.xfail
def test_factories():
    """Test the ability to create an object from one of a different type."""
    raise NotImplementedError


def test_additive(unitless: Objects, unitful: Objects):
    """Test additive operations between mixed object types."""
    operators = (standard.add, standard.sub)
    valid = (
        (unitful.scalar, unitful.vector, physical.Vector),
        (unitful.scalar, unitful.tensor, physical.Tensor),
        (unitful.vector, unitful.scalar, physical.Vector),
        (unitful.vector, unitful.tensor, physical.Tensor),
        (unitful.tensor, unitful.scalar, physical.Tensor),
        (unitful.tensor, unitful.vector, physical.Tensor),
        (unitful.scalar, unitful.array,  physical.Array),
        (unitful.tensor, unitful.array,  physical.Array),
        (unitful.array,  unitful.scalar, physical.Array),
        (unitful.array,  unitful.tensor, physical.Array),
    )
    for a, b, t in valid:
        for f in operators:
            r = f(a, b)
            assert isinstance(r, t)
            x = a.data.array if isinstance(a, physical.Array) else a.data
            y = b.data.array if isinstance(b, physical.Array) else b.data
            assert numpy.array_equal(r.data, f(x, y))
            assert r.unit == a.unit
    errors = (
        (unitful.scalar, unitless.vector, ValueError),
        (unitful.scalar, unitless.tensor, ValueError),
        (unitful.vector, unitless.scalar, ValueError),
        (unitful.vector, unitless.tensor, ValueError),
        (unitful.tensor, unitless.scalar, ValueError),
        (unitful.tensor, unitless.vector, ValueError),
        (unitful.scalar, unitless.array,  ValueError),
        (unitful.tensor, unitless.array,  ValueError),
        (unitful.vector, unitful.array,   TypeError),
        (unitful.array,  unitful.vector,  TypeError),
    )
    for a, b, error in errors:
        for f in operators:
            with pytest.raises(error):
                f(a, b)


def test_multiplicative(unitful: Objects):
    """Test multiplicative operations between mixed object types."""
    valid = (
        (unitful.scalar, unitful.vector, physical.Vector),
        (unitful.scalar, unitful.tensor, physical.Tensor),
        (unitful.vector, unitful.scalar, physical.Vector),
        (unitful.vector, unitful.tensor, physical.Tensor),
        (unitful.tensor, unitful.scalar, physical.Tensor),
        (unitful.tensor, unitful.vector, physical.Tensor),
        (unitful.scalar, unitful.array,  physical.Array),
        (unitful.vector, unitful.array,  physical.Array),
        (unitful.tensor, unitful.array,  physical.Array),
        (unitful.array,  unitful.scalar, physical.Array),
        (unitful.array,  unitful.vector, physical.Array),
        (unitful.array,  unitful.tensor, physical.Array),
    )
    operators = (
        (standard.mul, standard.mul),
        (standard.truediv, standard.truediv),
        (standard.floordiv, standard.truediv),
        (standard.mod, standard.truediv),
    )
    for a, b, t in valid:
        for f, g in operators:
            r = f(a, b)
            assert isinstance(r, t)
            x = a.data.array if isinstance(a, physical.Array) else a.data
            y = b.data.array if isinstance(b, physical.Array) else b.data
            assert numpy.array_equal(r.data, f(x, y))
            assert r.unit == g(a.unit, b.unit)
            if isinstance(r, physical.Array):
                if isinstance(a, physical.Array):
                    assert r.axes == a.axes
                if isinstance(b, physical.Array):
                    assert r.axes == b.axes


def test_pow(unitless: Objects, unitful: Objects):
    """Test exponentiation between mixed object types."""
    valid = (
        # can raise any unitless object by any unitless object
        (unitless.scalar, unitless.vector, physical.Vector),
        (unitless.scalar, unitless.tensor, physical.Tensor),
        (unitless.scalar, unitless.array,  physical.Array),
        (unitless.vector, unitless.scalar, physical.Vector),
        (unitless.vector, unitless.tensor, physical.Tensor),
        (unitless.vector, unitless.array,  physical.Array),
        (unitless.tensor, unitless.scalar, physical.Tensor),
        (unitless.tensor, unitless.vector, physical.Tensor),
        (unitless.tensor, unitless.array,  physical.Array),
        (unitless.array,  unitless.scalar, physical.Array),
        (unitless.array,  unitless.vector, physical.Array),
        (unitless.array,  unitless.tensor, physical.Array),
        # can raise any unitful object by a unitless scalar
        (unitful.vector,  unitless.scalar, physical.Vector),
        (unitful.tensor,  unitless.scalar, physical.Tensor),
        (unitful.array,   unitless.scalar, physical.Array),
    )
    f = standard.pow
    for a, b, t in valid:
        r = f(a, b)
        assert isinstance(r, t)
        x = a.data.array if isinstance(a, physical.Array) else a.data
        y = b.data.array if isinstance(b, physical.Array) else b.data
        assert numpy.array_equal(r.data, f(x, y))
        if a.isunitless and b.isunitless:
            assert r.unit == '1'
        else:
            assert r.unit == a.unit ** b.data
    error = (
        # cannot raise any object by any unitful object
        *tuple((i, j) for i in unitless for j in unitful),
        *tuple((i, j) for i in unitful for j in unitful),
        # cannot raise any object by a unitful vector
        *tuple((i, unitful.vector) for i in unitless),
        *tuple((i, unitful.vector) for i in unitful),
        # cannot raise any object by a unitful tensor
        *tuple((i, unitful.tensor) for i in unitless),
        *tuple((i, unitful.tensor) for i in unitful),
        # cannot raise any object by a unitful array
        *tuple((i, unitful.array) for i in unitless),
        *tuple((i, unitful.array) for i in unitful),
        # cannot raise any unitful object by even a unitless vector
        *tuple((i, unitless.vector) for i in unitful),
        # cannot raise any unitful object by even a unitless tensor
        *tuple((i, unitless.tensor) for i in unitful),
        # cannot raise any unitful object by even a unitless array
        *tuple((i, unitless.array) for i in unitful),
    )
    # These are all value errors because the value of the unit, not the presence
    # of that attribute, is the problem.
    for a, b in error:
        with pytest.raises(ValueError):
            f(a, b)


