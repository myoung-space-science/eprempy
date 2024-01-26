import pytest

from eprempy import physical
from eprempy import atomic


def test_create_species():
    """Test various ways to create an atomic species."""
    test = {
        'H': (1, 0),
        'H+': (1, 1),
        'He': (4, 0),
        'He+': (4, 1),
        'He++': (4, 2),
        'O--': (16, -2),
        'O-': (16, -1),
        'O': (16, 0),
        'O+': (16, 1),
        'O++': (16, 2),
    }
    for symbol, (amu, q) in test.items():
        from_symbol = atomic.species(symbol)
        from_values = atomic.species(mass=amu, charge=q)
        element = atomic.ELEMENTS.find(symbol.rstrip('-+'), unique=True)
        m = element['mass']
        for species in (from_symbol, from_values):
            assert species.symbol == symbol
            assert species.m == m
            assert species.mass == physical.scalar(m, unit='nuc')
            assert species.q == q
            assert species.charge == physical.scalar(q, unit='e')


# TODO: passing (mass: int, charge: int) to `elements` returns an int.
def test_elements():
    """Test the function that translates mass and charge to element symbol."""
    cases = [
        {'in': {'mass': 1, 'charge': 0}, 'out': ['H']},
        {'in': {'mass': [1], 'charge': [0]}, 'out': ['H']},
        {'in': {'mass': 1, 'charge': +1}, 'out': ['H+']},
        {'in': {'mass': 1, 'charge': -1}, 'out': ['H-']},
        {'in': {'mass': 4, 'charge': 0}, 'out': ['He']},
        {'in': {'mass': 4, 'charge': +1}, 'out': ['He+']},
        {'in': {'mass': 4, 'charge': +2}, 'out': ['He++']},
        {'in': {'mass': 16, 'charge': -2}, 'out': ['O--']},
        {'in': {'mass': [1, 4], 'charge': [+1, +2]}, 'out': ['H+', 'He++']},
    ]
    for case in cases:
        assert atomic.elements(**case['in']) == case['out']
    with pytest.raises(TypeError):
        atomic.elements(mass=[1], charge=[2, 3])
    with pytest.raises(atomic.MassValueError):
        atomic.elements(mass=[2], charge=[0])


