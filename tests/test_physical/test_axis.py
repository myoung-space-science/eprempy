import pytest

import numpy

from eprempy import measured
from eprempy import numeric
from eprempy import physical


def test_points():
    """Test the representation of an integral axis."""
    trivial = [
        range(5),
        tuple(range(5)),
        list(range(5)),
    ]
    for arg in trivial:
        points = physical.points(arg)
        assert points.index(2) == numeric.index.value(2)
        with pytest.raises(ValueError):
            points.index(6)
    points = physical.points([1, 10, 100, 1000, 10000])
    assert len(points) == 5
    sliced = points[1:4]
    assert sliced == physical.points([10, 100, 1000])
    assert numpy.all(sliced.indices == numeric.index.sequence(range(1, 4)))
    singular = points[1]
    assert singular == physical.points([10])
    assert numpy.all(singular.indices == numeric.index.sequence(1))
    assert points.index(10) == numeric.index.value(1)
    with pytest.raises(ValueError):
        points.index(0)


def test_symbols():
    """Test the representation of a symbolic axis."""
    letters = ['a', 'b0', 'c', 'x', 'z']
    symbols = physical.symbols(letters)
    assert len(symbols) == 5
    sliced = symbols[1:4]
    assert sliced == physical.symbols(letters[1:4])
    assert numpy.all(sliced.indices == numeric.index.sequence(range(1, 4)))
    singular = symbols[1]
    assert singular == physical.symbols(['b0'])
    assert numpy.all(singular.indices == numeric.index.sequence(1))
    for index, letter in enumerate(letters):
        assert symbols.index(letter) == numeric.index.value(index)
    errors = [
        ('A', ValueError),
        ('d', ValueError),
        (None, TypeError),
        (0, TypeError),
    ]
    for target, error in errors:
        with pytest.raises(error):
            symbols.index(target)


def test_coordinates():
    """Test the representation of a measured axis."""
    data = [-1.0, 1.0, 1.5, 2.0, 10.1]
    unit = 'm'
    array = measured.sequence(data, unit=unit)
    coordinates = physical.coordinates(array)
    assert len(coordinates) == 5
    sliced = coordinates[1:4]
    assert sliced == physical.coordinates(array[1:4])
    assert numpy.all(sliced.indices == numeric.index.sequence(range(1, 4)))
    singular = coordinates[1]
    assert singular == physical.coordinates(array[1])
    assert numpy.all(singular.indices == numeric.index.sequence(1))
    assert coordinates.unit == unit
    for index, value in enumerate(data):
        assert coordinates.index(value) == numeric.index.value(index)
    expected = numeric.index.sequence([0, 2])
    assert all(coordinates.index(-100.0, 150.0, 'cm') == expected)
    errors = [
        (-2.0, ValueError),
        (0.5, ValueError),
        ('1', TypeError),
        (None, TypeError),
    ]
    for target, error in errors:
        with pytest.raises(error):
            coordinates.index(target)
    assert coordinates.index(1.2, closest='lower') == numeric.index.value(1)
    assert coordinates.index(1.2, closest='upper') == numeric.index.value(2)
    assert coordinates.withunit('cm').data == coordinates.data.withunit('cm')
    assert coordinates.withunit('cm').index(150.0) == numeric.index.value(2)


