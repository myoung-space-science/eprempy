import pytest

from eprempy import metric


def test_system_factory():
    """Test the object that represents a system of quantities."""
    # Cases:
    # - length: same dimension; same unit.
    # - momentum: same dimension; different unit.
    # - magnetic induction: different dimension; different unit.
    cases = {
        'mks': {
            'length': {'dimension': 'L', 'unit': 'm'},
            'momentum': {'dimension': '(M * L) / T', 'unit': 'kg * m / s'},
            'magnetic induction': {'dimension': 'M / (T^2 * I)', 'unit': 'T'},
        },
        'cgs': {
            'length': {'dimension': 'L', 'unit': 'cm'},
            'momentum': {'dimension': '(M * L) / T', 'unit': 'g * cm / s'},
            'magnetic induction': {
                'dimension': 'M^1/2 / (L^1/2 * T)',
                'unit': 'G',
            },
        },
    }
    for string, quantities in cases.items():
        lower = string.lower()
        upper = string.upper()
        assert metric.system(lower) == metric.system(upper)
        system = metric.system(lower)
        for name, canonical in quantities.items():
            quantity = system[name]
            assert quantity.unit == canonical['unit']
            assert quantity.dimension == canonical['dimension']


def test_system_get_dimension():
    """Test the ability to compute a dimension from a unit."""
    cases = [
        {
            'unit': 'm',
            'systems': {'mks', 'cgs'},
            'quantity': 'length',
            'forms': ['L'],
        },
        {
            'unit': 'm / s',
            'systems': {'mks', 'cgs'},
            'quantity': 'velocity',
            'forms': ['L T^-1', 'T^-1 L'],
        },
        {
            'unit': 'km / s',
            'systems': {'mks', 'cgs'},
            'quantity': 'velocity',
            'forms': ['L T^-1', 'T^-1 L'],
        },
        {
            'unit': 'J',
            'systems': {'mks'},
            'quantity': 'energy',
            'forms': ['M L^2 T^-2', 'M T^-2 L^2', 'L^2 M T^-2'],
        },
        {
            'unit': 'erg',
            'systems': {'cgs'},
            'quantity': 'energy',
            'forms': ['M L^2 T^-2', 'M T^-2 L^2', 'L^2 M T^-2'],
        },
    ]
    for current in cases:
        unit = current['unit']
        forms = current['forms']
        for name in current['systems']:
            system = metric.system(name)
            for this in (unit, metric.unit(unit)):
                dimension = system.get_dimension(this)
                assert isinstance(dimension, metric.Dimension)
                for form in forms:
                    assert dimension == form


def test_system_unit_lookup():
    """Test the ability to retrieve the appropriate unit."""
    systems = {
        'mks': [
            ('quantity', 'length', 'm'),
            ('dimension', 'L', 'm'),
            ('unit', 'au', 'm'),
            ('dimension', '1', '1'),
            ('unit', '1', '1'),
            ('unit', 'erg', 'J'),
        ],
        'cgs': [
            ('quantity', 'length', 'cm'),
            ('dimension', 'L', 'cm'),
            ('unit', 'au', 'cm'),
            ('dimension', '1', '1'),
            ('unit', '1', '1'),
            ('unit', 'J', 'erg'),
        ],
    }
    for name, cases in systems.items():
        system = metric.system(name)
        for (key, test, expected) in cases:
            search = {key: test}
            assert system.get_unit(**search) == expected


def test_system_singleton():
    """Metric systems should be singletons of their lowercase name."""
    for system in ('mks', 'cgs'):
        original = metric.system(system)
        assert metric.system(original) is original
        for variation in (system.capitalize(), system.upper()):
            assert metric.system(variation) is original


def test_system_equality():
    """Test equality between a metric system and other objects."""
    never = {1, 1.0, '', 'system', None}
    for name in metric.SYSTEMS:
        for arg in {name.lower(), name.upper(), name.capitalize()}:
            system = metric.system(arg)
            for version in {name.lower(), name.upper(), name.capitalize()}:
                assert system == version
                for this in never:
                    assert system != this


def test_derived_quantity():
    """Make sure derived quantities have the correct attributes.
    
    A derived quantity (at least for the purposes of this test) is a
    symbolically defined metric quantity. For example, 'speed = length / time'
    is a derived quantity. Note that the definition of a derived quantity may
    contain derived quantities.
    """
    # TODO: Extend to all derived quantities.
    cases = {
        'area': {
            'mks': {
                'dimension': 'L^2',
                'unit': 'm^2',
            },
            'cgs': {
                'dimension': 'L^2',
                'unit': 'cm^2',
            },
        },
        'electric field': {
            'mks': {
                'dimension': '(M * L) / (T^3 * I)',
                'unit': 'V / m',
            },
            'cgs': {
                'dimension': 'M^1/2 / (T * L^1/2)',
                'unit': 'statV / cm',
            },
        },
        'fluence': {
            'mks': {
                'dimension': 'T^2 M^-1 L^-4',
                'unit': 'J^-1 sr^-1 m^-2',
            },
            'cgs': {
                'dimension': 'T^2 M^-1 L^-4',
                'unit': 'erg^-1 sr^-1 cm^-2',
            },
        },
        'flux': {
            'mks': {
                'dimension': 'T M^-1 L^-4',
                'unit': 'J^-1 s^-1 sr^-1 m^-2',
            },
            'cgs': {
                'dimension': 'T M^-1 L^-4',
                'unit': 'erg^-1 s^-1 sr^-1 cm^-2',
            },
        },
        'integral flux': {
            'mks': {
                'dimension': 'T^-1 L^-2',
                'unit': 's^-1 sr^-1 m^-2',
            },
            'cgs': {
                'dimension': 'T^-1 L^-2',
                'unit': 's^-1 sr^-1 cm^-2',
            },
        },
        'number density': {
            'mks': {
                'dimension': '1 / L^3',
                'unit': 'm^-3',
            },
            'cgs': {
                'dimension': '1 / L^3',
                'unit': 'cm^-3',
            },
        },
        'speed': {
            'mks': {
                'dimension': 'L / T',
                'unit': 'm / s',
            },
            'cgs': {
                'dimension': 'L / T',
                'unit': 'cm / s',
            },
        },
    }
    for name, systems in cases.items():
        quantity = metric.quantity(name)
        for system, expected in systems.items():
            assert quantity[system].dimension == expected['dimension']
            assert quantity[system].unit == expected['unit']


def test_quantity_factory():
    """Test the ability to represent arbitrary metric quantities.
    
    This test exists to test new derived quantities that have been built from
    those defined in the module.
    """
    q = metric.quantity('length / magnetic field')
    assert isinstance(q, metric.Quantity)
    assert q['mks'].unit == 'm T^-1'


def test_quantity_singleton():
    """Make quantities are singletons of their lowercase name."""
    original = metric.quantity('energy')
    for name in ('energy', 'Energy', 'ENERGY'):
        duplicate = metric.quantity(name)
        assert duplicate is original


def test_quantity_equality():
    """Test the definition of equality for a quantity."""
    names = [
        'length',
        'energy',
        'length / velocity',
    ]
    for name in names:
        q0 = metric.quantity(name)
        # It should be equal to its string name.
        assert q0 == name
        # Idempotence -> identity => equality.
        assert q0 == metric.quantity(name)


def test_quantity_equivalence():
    """Test the definition of equivalence between quantities."""
    pairs = [
        ('energy', 'work'),
        ('force * area / mass^2', 'volume / (time^2 * mass)'),
        ('frequency', 'vorticity'),
    ]
    for (s0, s1) in pairs:
        q0 = metric.quantity(s0)
        q1 = metric.quantity(s1)
        assert q0 != q1
        assert q0 | q1


def test_quantity_convert():
    """Test conversions with substitution within a quantity."""
    cases = {
        'length': {
            ('cm', 'mks'): 1e-2,
            ('m', 'cgs'): 1e2,
            ('mks', 'cm'): 1e2,
            ('cgs', 'm'): 1e-2,
            ('mks', 'cgs'): 1e2,
            ('cgs', 'mks'): 1e-2,
        },
        'momentum': {
            ('mks', 'cgs'): 1e5,
            ('cgs', 'mks'): 1e-5,
        },
        'energy': {
            ('mks', 'cgs'): 1e7,
            ('cgs', 'mks'): 1e-7,
            ('eV', 'mks'): 1.6022e-19,
            ('mks', 'eV'): 1 / 1.6022e-19,
            ('eV', 'cgs'): 1.6022e-12,
            ('cgs', 'eV'): 1 / 1.6022e-12,
        },
        'energy density': {
            ('mks', 'cgs'): 1e1,
            ('cgs', 'mks'): 1e-1,
        },
        'mass number': {
            ('nuc', 'mks'): 1.6605e-27,
            ('nuc', 'cgs'): 1.6605e-27,
        }
    }
    for name, current in cases.items():
        for (u0, u1), expected in current.items():
            quantity = metric.quantity(name)
            conversion = quantity.convert(u0).to(u1)
            assert float(conversion) == pytest.approx(expected)

