import pytest

import numpy

import support
from eprempy import measured
from eprempy import numeric
from eprempy import quantity


def test_implicitly_measurable(measurables):
    """Test the function that determines if we can measure an object."""
    true = [
        *[case['test'] for case in measurables],
        0,
        1,
    ]
    for this in true:
        assert quantity.ismeasurable(this)
    false = [
        None,
        '1',
        (),
        [],
        {},
        set(),
    ]
    for this in false:
        assert not quantity.ismeasurable(this)


def test_explicitly_measurable(measurables):
    """Test the function that determines if we can measure an object."""
    cases = [case['test'] for case in measurables]
    for case in cases:
        assert quantity.ismeasurable(case)
    assert quantity.ismeasurable(support.Measurable(1, unit='m / s'))


def test_parse(measurables):
    """Test the function that attempts to parse a measurable object."""
    for case in measurables:
        result = quantity.parse(case['test'])
        expected = case['full']
        assert result == expected
    for case in measurables:
        result = quantity.parse(case['test'], distribute=True)
        expected = case['dist']
        assert result == expected
    assert quantity.parse(0) == (0, '1') # zero is measurable!
    with pytest.raises(quantity.ParsingTypeError):
        quantity.parse(None)
    with pytest.raises(quantity.ParsingTypeError):
        quantity.parse(slice(None))
    with pytest.raises(quantity.ParsingValueError):
        quantity.parse([1.1, 'm', 2.3, 'cm'])
    with pytest.raises(quantity.ParsingValueError):
        quantity.parse([(1.1, 'm'), (2.3, 5.8, 'cm')])


def test_measure(measurables):
    """Test the function that creates a measurement from measurable input."""
    for case in measurables:
        result = quantity.measure(case['test'])
        assert isinstance(result, quantity.Measurement)
        assert tuple(result.data) == case['full'][:-1]
        assert result.unit == case['full'][-1]
        assert quantity.measure(result) is result
    this = support.Measurable([1], unit='m / s')
    expected = quantity.measurement([1], unit='m / s')
    assert quantity.measure(this) == expected
    strings = ['1.1', '2.3', 'm']
    expected = quantity.measurement([1.1, 2.3], unit='m')
    assert quantity.measure(strings) == expected
    expected = quantity.measurement([1.1, 2.3], unit='1')
    assert quantity.measure(strings[:-1]) == expected
    expected = quantity.measurement([1.1], unit='m')
    assert quantity.measure('1.1', 'm') == expected
    expected = quantity.measurement([1.1], unit='1')
    assert quantity.measure('1.1') == expected
    with pytest.raises(quantity.MeasuringTypeError):
        quantity.measure()


def test_isindexlike():
    """Test the function that checks for index-like input.

    Any instance of `~numeric.index.Object` or anything that can initialize an
    instance of `~numeric.index.Object` should test true. Anything else should
    test false.
    """
    true = [
        1,
        '1',
        numpy.array(1, dtype=int),
        measured.value(1),
        range(1, 2),
        [1],
        (1,),
        numpy.array([1], dtype=int),
        measured.sequence(1),
        range(1, 3),
        [1, 2],
        (1, 2),
        ['1', '2'],
        ('1', '2'),
        numpy.array([1, 2], dtype=int),
        measured.sequence([1, 2]),
        numpy.array([1, 2], ndmin=2),
        numpy.array([1, 2], ndmin=3),
        numpy.array([[1], [2]]),
        numeric.index.value(1),
        numeric.index.sequence([1, 2]),
    ]
    for case in true:
        assert quantity.isindexlike(case)
    false = [
        {1, 2},
        {1: 'a', 2: 'b'},
        slice(1, 3),
        measured.value(1, unit='m'),
        measured.sequence(1, unit='m'),
        measured.sequence([1, 2], unit='m'),
        numpy.array([[1, 2], [3, 4]]),
        measured.value(1, unit='m'),
        measured.sequence(1, unit='m'),
        1.0,
        '1.0',
        numpy.array(1, dtype=float),
        numpy.array([1], dtype=float),
        [1.0, 2],
        (1.0, 2),
        ['1.0', '2'],
        ('1.0', '2'),
        numpy.array([1, 2], dtype=float),
    ]
    for case in false:
        assert not quantity.isindexlike(case)


