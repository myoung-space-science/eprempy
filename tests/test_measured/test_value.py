"""
Tests of the `measured.Value` class.
"""

import numpy
import numpy.typing
import pytest

from eprempy import measured


def test_factory():
    """Test the ability to create a measured value."""
    value = 1.5
    unit = 'm'
    original = measured.value(value, unit=unit)
    copied = measured.value(original)
    assert copied is not original
    assert copied == original
    valid = [
        [value, unit],
        [measured.sequence([value], unit)],
        [measured.sequence([[value]], unit)],
        [numpy.array([[value]]), unit],
        [[value], unit],
        [[[value]], unit],
    ]
    for args in valid:
        assert measured.value(*args) == original
    error = [
        measured.sequence([value, 2*value]),
        measured.sequence([[value, 2*value]]),
        numpy.array([[value, 2*value]]),
        [[value, 2*value]],
        str(value),
        [str(value)],
        [[str(value)]],
    ]
    for arg in error:
        with pytest.raises(TypeError):
            measured.value(arg)
    with pytest.raises(ValueError):
        measured.value(original, unit=unit)


