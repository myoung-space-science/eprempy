import pytest

from eprempy import universal
from eprempy import physical


def test_constants():
    """Test the object that represents physical constants."""
    for key, this in universal.CONSTANTS.items(aliased=True):
        for system in ('mks', 'cgs'):
            mapping = universal.Constants(system)
            c = mapping[key]
            assert isinstance(c, universal.Constant)
            assert float(c) == float(this[system]['value'])
            assert c.unit == this[system]['unit']
            assert c.quantity == this['quantity']
            assert c.info == this['info']


def test_constant_asscalar():
    """Test the ability to convert a constant object to a physical scalar."""
    for key in universal.CONSTANTS.keys(aliased=True):
        for system in ('mks', 'cgs'):
            mapping = universal.Constants(system)
            c = mapping[key]
            s = c.asscalar
            assert isinstance(s, physical.Scalar)
            assert float(c) == float(s)


def test_elements():
    """Test the function that translates mass and charge to element symbol."""
    # TODO: This needn't test every possible charge state, and testing every
    # known element may be overkill, but it should extend beyond H and He.
    cases = [
        {'in': [1, 0], 'out': ['H']},
        {'in': [[1], [0]], 'out': ['H']},
        {'in': [1, +1], 'out': ['H+']},
        {'in': [1, -1], 'out': ['H-']},
        {'in': [4, 0], 'out': ['He']},
        {'in': [4, +1], 'out': ['He+']},
        {'in': [4, +2], 'out': ['He++']},
        {'in': [[1, 4], [+1, +2]], 'out': ['H+', 'He++']},
    ]
    for case in cases:
        assert universal.elements(*case['in']) == case['out']
    with pytest.raises(TypeError):
        universal.elements([1], [2, 3])
    with pytest.raises(universal.MassValueError):
        universal.elements([2], [0])


