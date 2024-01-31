import typing

import pytest

from eprempy import metric


C = metric._reference.C

@pytest.fixture
def conversions():
    """Test cases for unit conversions."""
    return {
        # Slot for temporary cases to run first, for the sake of simplifying
        # breakpoint debugging.
        'priority': {},
        # Length (common and simple)
        'length': {
            # trivial conversion
            ('m', 'm'): 1.0,
            # defined metric-system conversion
            ('m', 'cm'): 1e2,
            # base-unit rescale
            ('m', 'km'): 1e-3,
            # (same)
            ('m', 'mm'): 1e3,
            # (same)
            ('mm', 'm'): 1e-3,
            # to non-system unit
            ('m', 'au'): 1 / 1.495978707e11,
            # from non-system unit
            ('au', 'm'): 1.495978707e11,
            # trivial non-system conversion
            ('au', 'au'): 1.0,
        },
        # Momentum (requires symbolic expressions)
        'momentum': {
            # defined (forward)
            ('kg * m / s', 'g * cm / s'): 1e5,
            # defined (reverse)
            ('g * cm / s', 'kg * m / s'): 1e-5,
            # undefined (forward)
            ('g * km / s', 'g * cm / s'): 1e5,
            # undefined (reverse)
            ('g * cm / s', 'g * km / s'): 1e-5,
            # undefined (forward); non-system time unit
            ('g * km / day', 'g * cm / s'): 1e5 / 86400,
            # undefined (reverse); non-system time unit
            ('g * cm / s', 'g * km / day'): 86400 / 1e5,
            # equivalent expression with energy
            ('J s', 'kg m^2 s^-1'): 1.0,
        },
        # Energy (has multiple defined conversions)
        'energy': {
            # defined (forward)
            ('J', 'erg'): 1e7,
            # (same)
            ('eV', 'J'): 1.6022e-19,
            # defined (reverse)
            ('erg', 'J',): 1e-7,
            # (same)
            ('J', 'eV'): 1 / 1.6022e-19,
            # chained conversion
            ('eV', 'erg'): 1.6022e-12,
            # (same)
            ('erg', 'eV'): 1 / 1.6022e-12,
            # conversion with rescale
            ('MeV', 'J'): 1.6022e-13,
            # (same)
            ('J', 'MeV'): 1 / 1.6022e-13,
            # chained conversion with rescale
            ('MeV', 'erg'): 1.6022e-6,
            # (same)
            ('erg', 'MeV'): 1 / 1.6022e-6,
            # expansion
            ('J', 'kg m^2 s^-2'): 1.0,
            # chained conversion with expansion
            ('MeV', 'kg m^2 s^-2'): 1.6022e-13,
        },
        # Energy density (requires building quantity from formula)
        'energy density': {
            ('J / m^3', 'erg / cm^3'): 1e1,
            ('erg / cm^3', 'J / m^3'): 1e-1,
            ('J m^-3', 'erg cm^-3'): 1e1,
            ('m^-3 J', 'erg cm^-3'): 1e1,
            ('J m^-3', 'cm^-3 erg'): 1e1,
        },
        # Capacitance
        'capacitance': {
            # CGS unit is ambiguous
            ('F', 'cm'): C**2 * 1e-9,
            ('cm', 'F'): 1 / (C**2 * 1e-9),
        },
        # Conductance
        'conductance': {
            # CGS unit is ambiguous
            ('S', 'cm / s'): C**2 * 1e-5,
            ('cm / s', 'S'): 1 / (C**2 * 1e-5),
        },
        # Velocity
        'velocity': {
            # standard
            ('km/s', 'm/s'): 1e3,
            # non-system time unit
            ('km/h', 'km/s'): 1/3600,
            # variation on above
            ('m/h', 'cm/s'): 1/36,
        },
        # Decompositions of equivalent units
        'decompositions': {
            ('N', 'kg m s^-2'): 1.0,
            ('J', 'kg m^2 s^-2'): 1.0,
            ('V / m', 'T m s^-1'): 1.0,
        },
        # Common or pathological conversions
        'miscellaneous': {
            # length: meter -> solar radius (special case)
            ('Rs', 'm'): 6.96e8,
            # length: centimeter -> solar radius (chained special case)
            ('Rs', 'cm'): 6.96e10,
            # magnetic induction: cgs -> sim
            ('G', 'nT'): 1e5,
            # magnetic induction: sim -> cgs
            ('nT', 'G'): 1e-5,
            # terms in different order
            ('ms^3 m^-2', 'km^-2 s^3'): 1e-3,
            # above conversion with terms in same order
            ('ms^3 m^-2', 's^3 km^-2'): 1e-3,
            # particle distribution: sim -> mks
            ('s^3/km^6', 's^3/cm^6'): 1e-30,
            # particle distribution: terms in different order
            ('s^3 m^-6', 'km^-6 s^3'): 1e18,
            # particle flux: includes 'nuc' (dimensionless)
            (
                'm^-2 sr^-1 s^-1 J^-1',
                'cm^-2 sr^-1 s^-1 (MeV/nuc)^-1',
            ): 1.6022e-17,
            # particle flux: reduced energy term
            (
                'm^-4 sr^-1 s kg^-1',
                'cm^-2 sr^-1 s^-1 J^-1',
            ): 1e-4,
            # particle flux: reduced energy term with 'nuc'
            (
                'm^-4 sr^-1 s kg^-1',
                'cm^-2 sr^-1 s^-1 (MeV/nuc)^-1',
            ): 1.6022e-17,
            # particle fluence: (same)
            (
                's^2 kg^-1 sr^-1 m^-4',
                'cm^-2 sr^-1 (MeV/nuc)^-1',
            ): 1.6022e-17,
            # pseudo-conversion: mass number -> mass (MKS)
            ('nuc', 'kg'): 1.6605e-27,
            # pseudo-conversion: mass number -> mass (CGS)
            ('nuc', 'g'): 1.6605e-24,
        },
        # Equivalent unit in a different metric system
        'systems': {
            # unambiguous: G -> T
            ('G', 'mks'): 1e-4,
            # unambiguous: T -> G
            ('T', 'cgs'): 1e4,
        },
    }


# TODO: Consider porting cases from `test_systems.py::test_quantity_convert`.

def test_unit_to_unit(
    conversions: typing.Dict[str, typing.Dict[typing.Tuple[str, str], float]],
) -> None:
    """Test unit conversions in which the target is a unit."""
    valid = (v for k, v in conversions.items() if k != 'systems')
    for current in valid:
        for (u0, u1), factor in current.items():
            conversion = metric.conversion(u0, u1)
            assert float(conversion) == pytest.approx(factor)
            assert conversion.u0 == u0
            assert conversion.u1 == u1
    error = [
        # impossible conversion
        ('m', 'J'),
    ]
    for (u0, u1) in error:
        assert metric.conversion(u0, u1, error=False) is None
        with pytest.raises(metric.UnitConversionError):
            metric.conversion(u0, u1)


def test_unit_to_system(
    conversions: typing.Dict[str, typing.Dict[typing.Tuple[str, str], float]],
) -> None:
    """Test unit conversions in which the target is a metric system."""
    valid = (v for k, v in conversions.items() if k == 'systems')
    for current in valid:
        for (u, s), factor in current.items():
            conversion = metric.conversion(u, s)
            assert float(conversion) == pytest.approx(factor)
    error = {
        # ambiguous: 'cm / s' -> 'm / s' or 'S'
        ('cm / s', 'mks'): {
            'velocity': 1e-2,
            'conductance': 1 / (C**2 * 1e-5),
        },
    }
    for (u, s), quantity in error.items():
        assert metric.conversion(u, s, error=False) is None
        with pytest.raises(metric.UnitConversionError):
            metric.conversion(u, s)
        for name, factor in quantity.items():
            conversion = metric.conversion(u, s, quantity=name)
            assert float(conversion) == pytest.approx(factor)


