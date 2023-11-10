import pytest

from eprempy import symbolic
from eprempy import metric


def test_ratio():
    """Test the method that computes the ratio of two units."""
    cases = {
        ('cm', 'm'): 1e-2,
        ('m', 'cm'): 1e2,
        ('cm', 'cm'): 1.0,
        ('km', 'm'): 1e3,
        ('m', 'km'): 1e-3,
    }
    for (u0, u1), result in cases.items():
        assert metric.ratio(u0, u1) == result
    with pytest.raises(ValueError):
        metric.ratio('cm', 'J')


def test_identify():
    """Test the ability to identify arbitrary named units.

    Note that the primary role of this function is in support of the Unit class,
    so full coverage is not necessary as long as Unit is well tested.
    """
    order, unit = metric.identify('m')
    assert order.symbol == ''
    assert order.name == ''
    assert order.factor == 1.0
    assert unit.symbol == 'm'
    assert unit.name == 'meter'
    assert unit.quantity == 'length'
    order, unit = metric.identify('mm')
    assert order.symbol == 'm'
    assert order.name == 'milli'
    assert order.factor == 1e-3
    assert unit.symbol == 'm'
    assert unit.name == 'meter'
    assert unit.quantity == 'length'
    assert metric.identify('mm') == metric.identify('millimeter')
    order, unit = metric.identify('lm')
    assert order.symbol == ''
    assert order.name == ''
    assert order.factor == 1.0
    assert unit.symbol == 'lm'
    assert unit.name == 'lumen'
    assert unit.quantity == 'luminous flux'
    order, unit = metric.identify('MeV')
    assert order.symbol == 'M'
    assert order.name == 'mega'
    assert order.factor == 1e6
    assert unit.symbol == 'eV'
    assert unit.name == 'electronvolt'
    assert unit.quantity == 'energy'
    order, unit = metric.identify('μeV')
    assert order.symbol == 'μ'
    assert order.name == 'micro'
    assert order.factor == 1e-6
    assert unit.symbol == 'eV'
    assert unit.name == 'electronvolt'
    assert unit.quantity == 'energy'
    order, unit = metric.identify('uerg')
    assert order.symbol == 'μ'
    assert order.name == 'micro'
    assert order.factor == 1e-6
    assert unit.symbol == 'erg'
    assert unit.name == 'erg'
    assert unit.quantity == 'energy'
    order, unit = metric.identify('statA')
    assert order.symbol == ''
    assert order.name == ''
    assert order.factor == 1.0
    assert unit.symbol == 'statA'
    assert unit.name == 'statampere'
    assert unit.quantity == 'current'


def test_unitlike():
    """Test the instance check for unit-like objects."""
    valid = [
        'm',
        'm / s',
        'I am not a unit',
        '',
        metric.unit('km^2 * J / erg'),
        symbolic.expression('I am not a unit'),
    ]
    for this in valid:
        assert metric.unitlike(this)
    invalid = [
        False,
        True,
        int(3),
        float(3),
        complex(3),
        metric.dimension('L'),
    ]
    for this in invalid:
        assert not metric.unitlike(this)


@pytest.mark.xfail
def test_decomposition():
    """Test the module-level unit-decomposing function."""
    cases = {
        'm': {
            'mks': (1.0, 'm'),
            'cgs': (1e2, 'cm'),
        },
        'cm': {
            'mks': (1e-2, 'm'),
            'cgs': (1.0, 'cm'),
        },
        'J': {
            'mks': (1.0, 'kg m^2 s^-2'),
            'cgs': (1e1, 'g cm^2 s^-2'),
        },
        'erg': {
            'mks': (1e-1, 'kg m^2 s^-2'),
            'cgs': (1.0, 'g cm^2 s^-2'),
        },
        'N / cm^2': { # kg m s^-1 cm^-2
            'mks': (1e-4, 'kg s^-1 m^-1'), # kg m s^-1 (1e-2m)^-2
            'cgs': (1e-1, 'g s^-1 cm^-1'), # 1e-3g (1e2cm) s^-1 cm^-2
        },
        'erg * s / kg': {
            'mks': (),
            'cgs': (),
        },
    }
    for unit, systems in cases.items():
        for name, expected in systems.items():
            result = metric.reduction(unit, system=name)
            if expected is None:
                assert result is None
            else:
                (scale, expression) = expected
                assert symbolic.expression(result.units) == expression
                assert result.scale == scale
                assert result.system == name


