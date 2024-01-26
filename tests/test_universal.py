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

