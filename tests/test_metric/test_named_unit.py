import typing

import pytest

from eprempy import symbolic
from eprempy import metric
from eprempy.exceptions import UnitParsingError


def test_build_named_unit():
    cases = {
        'm': {
            'name': 'meter',
            'symbol': 'm',
            'scale': 1.0,
            'quantity': 'length',
        },
        'cm': {
            'name': 'centimeter',
            'symbol': 'cm',
            'scale': 1e-2,
            'quantity': 'length',
        },
        'J': {
            'name': 'joule',
            'symbol': 'J',
            'scale': 1.0,
            'quantity': 'energy',
        },
    }
    for name, attrs in cases.items():
        unit = metric.NamedUnit(name)
        for key, value in attrs.items():
            assert getattr(unit, key) == value
    with pytest.raises(UnitParsingError):
        metric.NamedUnit('cat')


def test_named_unit_dimensions():
    """Test the dimensions attribute of a NamedUnit."""
    cases = {
        'm': {'mks': 'L', 'cgs': 'L'},
        'cm': {'mks': 'L', 'cgs': 'L'},
        'J': {'mks': '(M * L^2) / T^2', 'cgs': None},
        'erg': {'cgs': '(M * L^2) / T^2', 'mks': None},
        'ohm': {'mks': 'M L^2 T^-3 I^-1', 'cgs': None},
        'au': {'mks': 'L', 'cgs': 'L'},
        'MeV': {'mks': '(M * L^2) / T^2', 'cgs': '(M * L^2) / T^2'},
    }
    for unit, dimensions in cases.items():
        named = metric.NamedUnit(unit)
        assert named.dimensions == dimensions
        named.dimensions.pop('mks')
        named.dimensions.pop('cgs')
        named.dimensions['foo'] = 'bar'
        assert named.dimensions == dimensions


def test_named_unit_conversion_factor():
    """Calling u0 >> u1 should compute the numerical conversion factor."""
    cases = {
        ('cm', 'm'): 1e-2,
        ('m', 'cm'): 1e+2,
        ('cm', 'cm'): 1.0,
        ('km', 'm'): 1e+3,
        ('m', 'km'): 1e-3,
    }
    for (s0, s1), expected in cases.items():
        u0 = metric.NamedUnit(s0)
        u1 = metric.NamedUnit(s1)
        # defined between instances
        u0_u1 = u0 >> u1
        assert u0_u1 == pytest.approx(expected)
        u1_u0 = u0 << u1
        assert u1_u0 == pytest.approx(1.0 / expected)
        # defined for instance >> string and string << instance
        u0_s1 = u0 >> s1
        assert u0_s1 == pytest.approx(expected)
        s1_u0 = u0 << s1
        assert s1_u0 == pytest.approx(1.0 / expected)
        # defined for string >> instance and instance << string
        s0_u1 = s0 >> u1
        assert s0_u1 == pytest.approx(expected)
        u1_s0 = s0 << u1
        assert u1_s0 == pytest.approx(1.0 / expected)
    with pytest.raises(ValueError):
        u0 = metric.NamedUnit('m')
        u1 = metric.NamedUnit('J')
        # not defined for different base units
        u0 >> u1
        u0 << u1


@pytest.fixture
def decompositions():
    """Test cases for named-unit decompositions."""
    return {
        # fundamental in mks and cgs
        's': [{'base': 's'}],
        # fundamental in mks
        'm': [{'base': 'm'}],
        'kg': [{'base': 'kg'}],
        'N': [
            {'base': 'kg', 'exponent': 1},
            {'base': 'm', 'exponent': 1},
            {'base': 's', 'exponent': -2},
        ],
        'J': [
            {'base': 'kg', 'exponent': 1},
            {'base': 'm', 'exponent': 2},
            {'base': 's', 'exponent': -2},
        ],
        'ohm': [
            {'base': 'kg', 'exponent': 1},
            {'base': 'm', 'exponent': 2},
            {'base': 's', 'exponent': -3},
            {'base': 'A', 'exponent': -1},
        ],
        # fundamental in cgs
        'cm': [{'base': 'cm'}],
        'g': [{'base': 'g'}],
        'dyn': [
            {'base': 'g', 'exponent': 1},
            {'base': 'cm', 'exponent': 1},
            {'base': 's', 'exponent': -2},
        ],
        'erg': [
            {'base': 'g', 'exponent': 1},
            {'base': 'cm', 'exponent': 2},
            {'base': 's', 'exponent': -2},
        ],
        # not fundamental in any metric system
        'mJ': None,
        'merg': None,
        'km': None,
        'au': None,
    }


def test_named_unit_decompose(decompositions: dict):
    """Test the NamedUnit.decompose method."""
    for unit, expected in decompositions.items():
        named = metric.NamedUnit(unit)
        result = named.decomposed
        if expected is None:
            assert result is None
        else:
            terms = [symbolic.term(**term) for term in expected]
            assert set(result) == set(terms)


@pytest.fixture
def reductions():
    """Test cases for named-unit reductions."""
    return {
        's': {
            'mks': {
                'scale': 1e0,
                'terms': [{'base': 's'}],
            },
            'cgs': {
                'scale': 1e0,
                'terms': [{'base': 's'}],
            },
        },
        'm': {
            'mks': {
                'scale': 1e0,
                'terms': [{'base': 'm'}],
            },
            'cgs': {
                'scale': 1e2,
                'terms': [{'base': 'cm'}],
            },
        },
        'cm': {
            'mks': {
                'scale': 1e-2,
                'terms': [{'base': 'm'}],
            },
            'cgs': {
                'scale': 1e0,
                'terms': [{'base': 'cm'}],
            },
        },
        'km': {
            'mks': {
                'scale': 1e3,
                'terms': [{'base': 'm'}],
            },
            'cgs': {
                'scale': 1e5,
                'terms': [{'base': 'cm'}],
            },
        },
        'kg': {
            'mks': {
                'scale': 1e0,
                'terms': [{'base': 'kg'}],
            },
            'cgs': {
                'scale': 1e3,
                'terms': [{'base': 'g'}],
            },
        },
        'g': {
            'mks': {
                'scale': 1e-3,
                'terms': [{'base': 'kg'}],
            },
            'cgs': {
                'scale': 1e0,
                'terms': [{'base': 'g'}],
            },
        },
        'J': {
            'mks': {
                'scale': 1e0,
                'terms': [
                    {'base': 'kg', 'exponent': 1},
                    {'base': 'm', 'exponent': 2},
                    {'base': 's', 'exponent': -2},
                ],
            },
            'cgs': None,
        },
        'mJ': {
            'mks': {
                'scale': 1e-3,
                'terms': [
                    {'base': 'kg', 'exponent': 1},
                    {'base': 'm', 'exponent': 2},
                    {'base': 's', 'exponent': -2},
                ],
            },
            'cgs': None,
        },
        'erg': {
            'mks': None,
            'cgs': {
                'scale': 1e0,
                'terms': [
                    {'base': 'g', 'exponent': 1},
                    {'base': 'cm', 'exponent': 2},
                    {'base': 's', 'exponent': -2},
                ],
            },
        },
        'merg': {
            'mks': None,
            'cgs': {
                'scale': 1e-3,
                'terms': [
                    {'base': 'g', 'exponent': 1},
                    {'base': 'cm', 'exponent': 2},
                    {'base': 's', 'exponent': -2},
                ],
            },
        },
        'N': {
            'mks': {
                'scale': 1e0,
                'terms': [
                    {'base': 'kg', 'exponent': 1},
                    {'base': 'm', 'exponent': 1},
                    {'base': 's', 'exponent': -2},
                ],
            },
            'cgs': None,
        },
        'au': {
            'mks': None,
            'cgs': None,
        },
    }


def test_reduction_class():
    """Test the symbolic expression of a unit reduction."""
    this = metric.Reduction(['m^2'], scale=2, system='mks')
    assert this.units == ['m^2']
    assert this.scale == 2.0
    assert this.system == 'mks'
    new = 3 * this
    assert new.units == ['m^2']
    assert new.scale == 6.0
    assert new.system == 'mks'
    new = this * 2
    assert new.units == ['m^2']
    assert new.scale == 4.0
    assert new.system == 'mks'
    new = this / 4
    assert new.units == ['m^2']
    assert new.scale == 0.5
    assert new.system == 'mks'
    with pytest.raises(TypeError):
        5 / this
    new = this ** 2
    assert new.units == ['m^4']
    assert new.scale == 4.0
    assert new.system == 'mks'
    with pytest.raises(TypeError):
        3 ** this


def test_named_unit_norm():
    """A named unit should know its canonical equivalents."""
    cases = {
        'm': {
            'mks': 'm',
            'cgs': 'cm',
        },
        'cm': {
            'mks': 'm',
            'cgs': 'cm',
        },
        'J': {
            'mks': 'J',
            'cgs': 'erg',
        },
        'mJ': {
            'mks': 'J',
            'cgs': 'erg',
        },
        'erg': {
            'mks': 'J',
            'cgs': 'erg',
        },
        'kerg': {
            'mks': 'J',
            'cgs': 'erg',
        },
        'eV': {
            'mks': 'J',
            'cgs': 'erg',
        },
        'MeV': {
            'mks': 'J',
            'cgs': 'erg',
        },
    }
    for unit, systems in cases.items():
        named = metric.NamedUnit(unit)
        for system, expected in systems.items():
            assert named.norm[system] == expected


def test_named_unit_reduce(
    reductions: typing.Dict[str, typing.Dict[str, typing.Any]],
) -> None:
    """Test the NamedUnit.reduce method."""
    for unit, systems in reductions.items():
        named = metric.NamedUnit(unit)
        for system, expected in systems.items():
            result = named.reduce(system)
            if expected is None:
                assert result is None
            else:
                assert result.system == system
                assert result.scale == expected['scale']
                terms = [symbolic.term(**term) for term in expected['terms']]
                assert set(result.units) == set(terms)


def test_named_unit_reduce_system(
    reductions: typing.Dict[str, typing.Dict[str, typing.Any]],
) -> None:
    """Test reductions with the default metric system."""
    these = {
        'J': 'mks', # only defined in mks
        'erg': 'cgs', # only defined in cgs
        'cm': 'cgs', # fundamental in cgs
        'kg': 'mks', # fundamental in mks
        's': 'mks', # fundamental in both
        'au': 'mks', # fundamental in neither
    }
    for unit, default in these.items():
        case = reductions[unit][default]
        result = metric.NamedUnit(unit).reduce()
        if case is None:
            assert result is None
        else:
            assert result.system == default
            terms = [symbolic.term(**term) for term in case['terms']]
            assert result.scale == case['scale']
            assert set(result.units) == set(terms)


def test_named_unit_systems():
    """Determine which metric systems include a named unit."""
    test = {
        'm': {
            'allowed': {'mks', 'cgs'},
            'defined': {'mks', 'cgs'},
            'fundamental': {'mks'},
        },
        'cm': {
            'allowed': {'mks', 'cgs'},
            'defined': {'mks', 'cgs'},
            'fundamental': {'cgs'},
        },
        'J': {
            'allowed': {'mks'},
            'defined': {'mks'},
            'fundamental': {'mks'},
        },
        'erg': {
            'allowed': {'cgs'},
            'defined': {'cgs'},
            'fundamental': {'cgs'},
        },
        'au': {
            'allowed': {'mks', 'cgs'},
            'defined': set(),
            'fundamental': set(),
        },
        's': {
            'allowed': {'mks', 'cgs'},
            'defined': {'mks', 'cgs'},
            'fundamental': {'mks', 'cgs'},
        },
    }
    for unit, cases in test.items():
        for mode, expected in cases.items():
            named = metric.NamedUnit(unit)
            assert set(named.systems[mode]) == expected
            named.systems.pop('allowed')
            named.systems['foo'] = 'bar'
            assert set(named.systems[mode]) == expected


def test_named_unit_idempotence():
    """Make sure we can create a new NamedUnit from an existing instance."""
    old = metric.NamedUnit('m')
    new = metric.NamedUnit(old)
    assert isinstance(new, metric.NamedUnit)
    assert new is old


def test_named_unit_singleton():
    """Make sure named units act like singletons."""
    m = metric.NamedUnit('m')
    assert metric.NamedUnit('meter') is m
    cm = metric.NamedUnit('cm')
    assert m is not cm
    assert metric.NamedUnit('centimeter') is cm


