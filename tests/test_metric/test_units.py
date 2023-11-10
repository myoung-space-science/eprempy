import operator

import pytest

from eprempy import symbolic
from eprempy import metric


def test_unit_factory():
    """Initialize a metric unit with various strings."""
    strings = {
        'm': {
            'unit': 'm',
            'dimension': 'L',
        },
        'm / s': {
            'unit': 'm s^-1',
            'dimension': 'L T^-1',
        },
        '1 / s': {
            'unit': 's^-1',
            'dimension': 'T^-1',
        },
        '1 / s^2': {
            'unit': 's^-2',
            'dimension': 'T^-2',
        },
        's^3 / km^6': {
            'unit': 's^3 km^-6',
            'dimension': 'T^3 L^-6',
        },
        '# / (cm^2*s*sr*MeV/nuc)': {
            'unit': '# cm^-2 s^-1 sr^-1 (MeV nuc^-1)^-1',
            'dimension': 'L^-2 T^-1 (M L^2 T^-2 M^-1)^-1',
        },
        '# / ((cm^2*s*sr*MeV/nuc))': {
            'unit': '# cm^-2 s^-1 sr^-1 (MeV nuc^-1)^-1',
            'dimension': 'L^-2 T^-1 (M L^2 T^-2 M^-1)^-1',
        },
    }
    for arg, expected in strings.items():
        unit = metric.unit(arg)
        assert unit == expected['unit']


def test_unit_singleton():
    """Make sure a unit acts like a singleton of its expression string."""
    args = [
        'kg m^2 / s^2',
        'kg m^2 s^-2',
        'kg s^-2 m^2',
        'm^2 s^-2 kg',
        'm^2 kg s^-2',
        's^-2 kg m^2',
        's^-2 m^2 kg',
    ]
    original = metric.unit(args[0])
    for arg in args[1:]:
        assert metric.unit(arg) is original


def test_unit_idempotence():
    """Make sure initializing with a Unit creates a new Unit."""
    old = metric.unit('m')
    new = metric.unit(old)
    assert isinstance(new, metric.Unit)
    assert str(new) == str(old)
    assert repr(new) == repr(old)


def test_unit_normalize():
    """User must be able to normalize a given unit to a metric system."""
    cases = {
        # high-priority examples from EPREM
        'day': {
            'mks': 's',
            'cgs': 's',
        },
        'au': {
            'mks': 'm',
            'cgs': 'cm',
        },
        'km / s': {
            'mks': 'm / s',
            'cgs': 'cm / s',
        },
        'MeV': {
            'mks': 'J',
            'cgs': 'erg',
        },
        'nT': {
            'mks': 'T',
            'cgs': 'G',
        },
        'cm^-3': {
            'mks': 'm^-3',
            'cgs': 'cm^-3',
        },
        's^3 / km^6': {
            'mks': 's^3 / m^6',
            'cgs': 's^3 / cm^6',
        },
    }
    for name, systems in cases.items():
        unit = metric.unit(name)
        for system, expected in systems.items():
            assert unit.normalize(system) == expected


def test_unit_quantity():
    """A Unit should know its equivalent physical quantity."""
    test = {
        'length': ('m', 'cm', 'au'),
        'length / time': ('m / s', 'cm / s', 'au / s'),
        'energy': ('J', 'kJ', 'erg', 'eV'),
        'temperature': ('K', 'mK'),
        'potential': ('V', 'mV', 'statV'),
        'mass * length / time': ('kg * m / s', 'mg * au / day', 'g * cm / s'),
        # 'momentum': ('kg * m / s', 'mg * au / day', 'g * cm / s'),
        # 'mass density': ('kg / cm^3', 'g / au^3'),
    }
    for quantity, units in test.items():
        for unit in units:
            assert metric.unit(unit).quantity == quantity


def test_unit_dimensions():
    """A Unit should know its dimension in all applicable metric systems."""
    test = {
        'm': { # 'm' is defined in both systems
            'mks': 'L',
            'cgs': 'L',
        },
        'm / s': { # 'm' and 's' are defined in both systems
            'mks': 'L T^-1',
            'cgs': 'L T^-1',
        },
        'J': { # 'J' is defined only in mks
            'mks': 'M L^2 T^-2',
            'cgs': None,
        },
        'erg': { # 'erg' is defined only in cgs
            'mks': None,
            'cgs': 'M L^2 T^-2',
        },
        'au': { # 'au' is system-independent
            'mks': 'L',
            'cgs': 'L',
        },
        '# / (cm^2 s sr J)': { # mix of both ('cm') and mks ('J')
            'mks': 'T M^-1 L^-4',
            'cgs': 'T M^-1 L^-4',
        },
        '# / (m^2 s sr erg)': { # mix of both ('m') and cgs ('erg')
            'mks': 'T M^-1 L^-4',
            'cgs': 'T M^-1 L^-4',
        },
        '# / (cm^2 s sr MeV)': { # mix of cgs ('cm') and none ('MeV')
            'mks': 'T M^-1 L^-4',
            'cgs': 'T M^-1 L^-4',
        },
        'au / m': { # dimensionless mix of none ('au') and both ('m')
            'mks': '1',
            'cgs': '1',
        },
        'au / cm': { # dimensionless mix of none ('au') and both ('cm')
            'mks': '1',
            'cgs': '1',
        },
        'J / erg': { # dimensionless mix of mks ('J') and cgs ('erg')
            'mks': '1',
            'cgs': '1',
        },
        'J / eV': { # dimensionless mix of mks ('J') and none ('eV')
            'mks': '1',
            'cgs': '1',
        },
        'erg / eV': { # dimensionless mix of cgs ('erg') and none ('eV')
            'mks': '1',
            'cgs': '1',
        },
    }
    for string, cases in test.items():
        unit = metric.unit(string)
        for system, expected in cases.items():
            assert unit.dimensions[system] == expected
    # User should not be able to alter dimensions on an instance.
    meter = metric.unit('m')
    with pytest.raises(AttributeError):
        meter.dimensions.pop('mks')
    with pytest.raises(TypeError):
        meter.dimensions['mks'] = 'Oops!'
    assert meter.dimensions['mks'] == 'L'


def test_decompose_unit():
    """Test the ability to decompose a unit expression."""
    cases = {
        'm': 'm',
        'cm': 'cm',
        'km': 'km',
        'au': 'au',
        'm / cm': 'm / cm',
        'm / au': 'm / au',
        'N * s': 'kg m s^-1',
        'N / s': 'kg m s^-3',
        'N / m': 'kg s^-2',
        'N * s^2': 'kg m',
        'N / cm': 'kg m s^-2 cm^-1',
        'J / erg': 'kg m^2 g^-1 cm^-2',
        'J * (kg / s) / N^2': 's',
    }
    for unit, expected in cases.items():
        expression = symbolic.expression(expected)
        assert metric.unit(unit).decomposed == expression


def test_unit_algebra():
    """Test symbolic operations on the Unit class."""
    u0 = metric.unit('m')
    u1 = metric.unit('J')
    assert u0**2 is not u0
    assert u0 * u1 == metric.unit('m * (kg * m^2 / s^2)')
    assert u0 / u1 == metric.unit('m / (kg * m^2 / s^2)')
    assert u0**2 / u1**3 == metric.unit('m^2 / (kg * m^2 / s^2)^3')
    assert (u0 / u1)**2 == metric.unit('m^2 / (kg * m^2 / s^2)^2')


def test_unit_multiply():
    """Test the ability to create a new compound unit with '*'."""
    cases = {
        ('m', 's'): 'm * s',
        ('m / s', 'km / m'): 'km / s',
        ('m', 'm'): 'm^2',
        ('m', 'm^-1'): '1',
        ('N', '(kg * m / s^2)^-1'): '1',
        ('N', 'kg * m / s^2'): 'kg^2 * m^2 / s^4',
        ('J * cm', 'erg * m'): 'kg m^3 g cm^3 s^-4',
        ('J', 'm'): 'kg m^3 s^-2',
        ('N / erg', 'J / dyn'): 'kg^2 m^3 g^-2 cm^-3',
        ('N / cm^3', 'erg * s / kg'): 'm * g / (s^3 * cm)',
        (1 , 'm / s'): 'm / s',
        ('m / s' , 1): 'm / s',
    }
    apply_multiplicative(operator.mul, cases)
    with pytest.raises(ValueError):
        2 * metric.unit('m / s')
    with pytest.raises(ValueError):
        metric.unit('m / s') * 2


def test_unit_divide():
    """Test the ability to create a new compound unit with '/'."""
    cases = {
        ('m', 's'): 'm / s',
        ('m / s', 'm / km'): 'km / s',
        ('m', 'm'): '1',
        ('m', 'm^-1'): 'm^2',
        ('N', '(kg * m / s^2)^-1'): 'kg^2 * m^2 / s^4',
        ('N', 'kg * m / s^2'): '1',
        ('J * cm', 'erg * m'): 'kg m g^-1 cm^-1',
        ('J', 'm'): 'kg m s^-2',
        ('N / erg', 'J / dyn'): 'cm^-1 m^-1',
        ('N / cm^3', 'erg * s / kg'): 'kg^2 * m / (g * cm^5 * s)',
        (1 , 'm / s') : 's / m',
        ('m / s' , 1) : 'm / s',
    }
    apply_multiplicative(operator.truediv, cases)
    with pytest.raises(ValueError):
        2 / metric.unit('m / s')
    with pytest.raises(ValueError):
        metric.unit('m / s') / 2


def apply_multiplicative(opr, cases: dict):
    """Apply a multiplicative operator between units."""
    for (this, that), expected in cases.items():
        operands = (
            (metric.unit(this), metric.unit(that)),
            (this, metric.unit(that)),
            (metric.unit(this), that),
        )
        for a, b in operands:
            result = opr(a, b)
            assert isinstance(result, metric.Unit)
            assert result == expected
            assert result is metric.unit(expected)


def test_unit_conversion_factor():
    """Test conversion with the Unit class."""
    unit = metric.unit('m')
    assert unit >> metric.unit('cm') == 1e2
    assert 'cm' >> unit == 1e-2
    assert unit >> 'cm' == 1e2
    unit = metric.unit('m / s')
    assert 'km / h' >> unit == pytest.approx(1e3 / 3600)
    assert unit >> 'km / h' == pytest.approx(3600 / 1e3)


def test_unit_raise():
    """Test the ability to create a new compound unit with '**'."""
    cases = {
        ('m', 2): 'm^2',
        ('m / s', 3): 'm^3 s^-3',
        ('J', 2): 'J^2',
        ('J * s^2 / m^3', -1): 'J^-1 s^-2 m^3',
    }
    for (this, that), expected in cases.items():
        result = metric.unit(this) ** that
        assert isinstance(result, metric.Unit)
        assert result == metric.unit(expected)


def test_unit_consistency():
    """Test the ability to check if two units are mutually consistent."""
    cases = {
        ('m', 'm'): True,
        ('m', 'cm'): True,
        ('m', 'km'): True,
        ('m', 'au'): True,
        ('cm', 'km'): True,
        ('cm', 'au'): True,
        ('J', 'erg'): True,
        ('J', 'eV'): True,
        ('erg', 'eV'): True,
        ('J', 'N * m'): True,
        ('J', 'N'): False,
        ('N', 'm'): False,
        ('V', 'statV'): True,
        ('C', 'statC'): True,
        ('T', 'G'): True,
        ('nuc', 'kg'): True,
    }
    for (u0, u1), truth in cases.items():
        assert (metric.unit(u0) | metric.unit(u1)) == truth
        assert (metric.unit(u0) | u1) == truth
        assert (u0 | metric.unit(u1)) == truth


def test_unit_equivalence():
    """Test the definition of equivalence between units."""
    cases = {
        # equality implies equivalence
        ('m / s', 'm s^-1'): True,
        # units that differ only by dimensionless terms are equivalent
        ('# / (m^2 s sr J)', 'm^-2 s^-1 sr^-1 J^-1'): True,
        ('# / (m^2 s sr J)', '1 / (m^2 s sr J)'): True,
        # physically equivalent units are equivalent
        ('N', 'kg m s^-2'): True,
        ('dyn', 'g cm s^-2'): True,
        ('m^3 / (s^2 * kg)', 'm^2 N kg^-2'): True,
        # a ratio of equal units is unitless
        ('J / J', '1'): True,
        # units of the same quantity are not necessarily equivalent
        ('N', 'dyn'): False,
        ('N', 'g cm s^-2'): False,
        # units that are not interchangeable are not equivalent
        ('N', 'kg m^2 s^-2'): False,
        # A dimensioned unit is not equivalent to the dimensionless unit
        ('m', '1'): False,
        ('day', '1'): False,
        # miscellaneous pathological cases
        ('au', 'cd * sr'): False,
    }
    for (u0, u1), truth in cases.items():
        assert (metric.unit(u0) & metric.unit(u1)) == truth
        assert (metric.unit(u0) & u1) == truth
        assert (u0 & metric.unit(u1)) == truth


def test_unit_equality():
    """Test the definition of strict equality between units."""
    cases = {
        # identity implies equality
        ('m / s', 'm / s'): True,
        # units with equivalent string expressions are equal
        ('m / s', 'm s^-1'): True,
    }
    for (u0, u1), truth in cases.items():
        assert (metric.unit(u0) == metric.unit(u1)) == truth
        assert (metric.unit(u0) == u1) == truth
        assert (u0 == metric.unit(u1)) == truth


def test_unit_identity():
    """Instances that represent the same unit should be identical"""
    cases = [
        ('m', 'meter'),
        ('J', 'joule'),
        ('eV', 'electronvolt'),
        ('G', 'gauss'),
        ('T', 'tesla'),
        ('s', 'second'),
        ('rad', 'radian'),
        ('deg', 'degree'),
        ('Hz', 'hertz'),
        ('meter / second', 'm / s'),
        ('kilojoule * cm', 'kJ * cm'),
    ]
    for (u0, u1) in cases:
        assert metric.unit(u0) is metric.unit(u1)


def test_unit_dimensionless():
    """Test the boolean `dimensionless` property."""
    cases = {
        '1': True,
        '#': True,
        'm': False,
        'cm': False,
        'J': False,
        'erg': False,
        'N / N': True,
    }
    for unit, truth in cases.items():
        assert metric.unit(unit).dimensionless == truth


def test_unit_standardize():
    """Test the helper function that standardizes unit strings."""
    cases = {
        'julian date': 'day',
        'shell': '1',
        'cos(mu)': '1',
        'e-': 'e',
        '# / cm^2 s sr MeV': '# / (cm^2 s sr MeV/nuc)',
    }
    for old, new in cases.items():
        assert metric.standardize(old) == new


