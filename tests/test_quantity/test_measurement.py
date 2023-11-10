import numpy
import numpy.typing
import pytest

from eprempy import measured
from eprempy import quantity


def test_scalar_measurement():
    """Test a scalar-like measurement."""
    value = 1.5
    unit = 'm / s'
    x = quantity.measurement(1.5, unit=unit)
    assert len(x) == 1
    assert x.size == 1
    assert list(x) == [measured.value(value, unit=unit)]
    assert x[0] == measured.value(value, unit=unit)
    assert x.unit == unit
    assert float(x) == float(value)
    assert int(x) == int(value)
    assert isinstance(numpy.array(x), numpy.ndarray)
    assert numpy.array_equal(x, [value])


def test_vector_measurement():
    """Test a vector-like measurement."""
    value = 1.5
    values = [value, value]
    unit = 'm / s'
    x = quantity.measurement(values, unit=unit)
    assert len(x) == 2
    assert x.size == 2
    assert list(x) == [measured.value(v, unit=unit) for v in values]
    for i in (0, 1):
        assert x[i] == measured.value(value, unit=unit)
    assert x.unit == unit
    with pytest.raises(TypeError):
        float(x)
    with pytest.raises(TypeError):
        int(x)
    assert isinstance(numpy.array(x), numpy.ndarray)
    assert numpy.array_equal(x, values)


def test_array_measurement():
    """Test an array-like measurement."""
    value = 1.5
    values = [[value, value], [value, value]]
    unit = 'm / s'
    # Create an instance from nested lists.
    x = quantity.measurement(values, unit=unit)
    assert len(x) == 2
    assert x.size == 4
    for i in (0, 1):
        for j in (0, 1):
            assert x[i][j] == measured.value(value, unit=unit)
    with pytest.raises(TypeError):
        float(x)
    with pytest.raises(TypeError):
        int(x)
    assert isinstance(numpy.array(x), numpy.ndarray)
    assert numpy.array_equal(x, values)
    array = numpy.array(values)
    # Create an instance from a numpy array.
    y = quantity.measurement(array, unit=unit)
    assert len(y) == 2
    assert y.size == 4
    for i in (0, 1):
        for j in (0, 1):
            assert y[i, j] == measured.value(value, unit=unit)
    with pytest.raises(TypeError):
        float(y)
    with pytest.raises(TypeError):
        int(y)
    assert numpy.asarray(y) is y.data
    assert numpy.array(y) is not y.data


def test_measurement_unit_update():
    """Test unit conversion on a metric measurement."""
    a = quantity.measurement(2.0, unit='m')
    # Change the unit of the original measurement.
    b = a.withunit('cm')
    assert isinstance(b, quantity.Measurement)
    assert b is not a
    assert b.data == [200.0]
    assert b.unit == 'cm'
    assert a.data == [2.0]
    assert a.unit == 'm'
    # Change it again on the original measurement.
    c = a.withunit('km')
    assert isinstance(c, quantity.Measurement)
    assert c is not a
    assert c.data == [2e-3]
    assert c.unit == 'km'
    assert a.data == [2.0]
    assert a.unit == 'm'
    # Change it again on the secondary measurement.
    d = b.withunit('km')
    assert isinstance(d, quantity.Measurement)
    assert d is not b
    assert d.data == [2e-3]
    assert d.unit == 'km'
    assert b.data == [200.0]
    assert b.unit == 'cm'


