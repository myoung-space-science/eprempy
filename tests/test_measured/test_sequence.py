"""
Tests of the `measured.Sequence` class.
"""

import numpy
import numpy.typing
import pytest

from eprempy import measured


def test_factory():
    """Test the ability to create a measured sequence."""
    value = 1.5
    unit = 'm'
    values = [value, 2*value]
    for arg in (values, [values]):
        sequence = measured.sequence(arg, unit)
        copied = measured.sequence(sequence)
        assert copied is not sequence
        assert copied == sequence
    valid = [
        (
            [value, unit],
            measured.sequence([value], unit),
        ),
        (
            [measured.value(value, unit)],
            measured.sequence([value], unit),
        ),
        (
            [numpy.array([value]), unit],
            measured.sequence([value], unit),
        ),
        (
            [numpy.array([values]), unit],
            measured.sequence(values, unit),
        ),
        (
            [numpy.array([values, values]), unit],
            measured.sequence([values, values], unit)
        ),
        (
            [measured.sequence(numpy.array([value]), unit)],
            measured.sequence([value], unit),
        ),
        (
            [values, unit],
            measured.sequence(values, unit),
        ),
        (
            [values, unit],
            measured.sequence(values, unit),
        ),
        (
            [measured.value(value, unit)],
            measured.sequence([value], unit),
        ),
    ]
    for (args, expected) in valid:
        assert measured.sequence(*args) == expected
    with pytest.raises(ValueError):
        measured.sequence(sequence, unit=unit)


def test_subscription():
    """Test the behavior of a subscripted measured sequence."""
    data = numpy.arange(10, dtype=float)
    unit = 'm'
    original = measured.sequence(data, unit=unit)
    sequence = original[1:4]
    assert isinstance(sequence, measured.Sequence)
    assert numpy.array_equal(sequence.data, data[1:4])
    assert sequence.unit == unit
    value = original[4]
    assert isinstance(value, measured.Value)
    assert value.data == data[4]
    assert value.unit == unit


