import numpy

from eprempy import dataset


def test_array_factory():
    """Test the ability to create a core array."""
    data = numpy.arange(3 * 4).reshape(3, 4)
    unit = 'm'
    dimensions = ('x', 'y')
    array = dataset.array(data=data, unit=unit, dimensions=dimensions)
    assert isinstance(array.data, numpy.ndarray)
    assert isinstance(array.unit, str)
    assert array.unit == unit
    assert array.dimensions == dimensions


def test_scalar_factory():
    """Test the ability to create a core scalar."""
    value = 2.0
    unit = 'J'
    scalar = dataset.scalar(value=value, unit=unit)
    assert scalar.value == value
    assert scalar.unit == unit


def test_axis_factory():
    """Test the ability to create a core axis."""
    size = 10
    axis = dataset.axis(size=size)
    assert isinstance(axis.size, int)
    assert axis.size == size


