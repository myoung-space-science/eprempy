import numpy

from eprempy import numeric


def test_data_isclose():
    """Test the function that checks for a value that is "close enough"."""
    this = numeric.Object(numpy.array([1.1e-30, 2e-30]))
    tests = [
        {'value': 1.1e-30,     'in': True,  'contains': True},
        {'value': 2.0e-30,     'in': True,  'contains': True},
        {'value': 1.99999e-30, 'in': False, 'contains': True},
    ]
    for test in tests:
        assert (test['value'] in this.data) == test['in']
        assert numeric.data.isclose(this, test['value']) == test['contains']
    value = 1.99999e-30
    scalar = numeric.Object(2.0e-30)
    assert value != scalar
    assert numeric.data.isclose(scalar, value)


def test_data_hasdtype():
    """Test the function that checks a data object's dtype."""
    this = numeric.Object([1.5, 3])
    assert numeric.data.hasdtype(this, numpy.floating)


def test_data_isequal(object_factory):
    """Test the function that checks for numericly equal objects."""
    values = [
        1.5,
        numpy.array([1.5]),
        numpy.array([1.5, -1.5]),
    ]
    for v in values:
        x = object_factory(v, color='red')
        y = object_factory(v, color='blue')
        assert x != y
        assert numeric.data.isequal(x, v)
        assert numeric.data.isequal(y, v)
        assert numeric.data.isequal(v, x)
        assert numeric.data.isequal(v, y)
        assert numeric.data.isequal(v, v)
        assert numeric.data.isequal(x, y)
        assert numeric.data.isequal(x, y)


