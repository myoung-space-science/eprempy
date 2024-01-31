"""
All independently defined variables for the `metric` namespace.
"""

import typing

import numpy

from .. import aliased
from .. import container


T = typing.TypeVar('T')


_PREFIXES = [
    {'symbol': 'Y', 'name': 'yotta', 'factor': 1e+24},
    {'symbol': 'Z', 'name': 'zetta', 'factor': 1e+21},
    {'symbol': 'E', 'name': 'exa', 'factor': 1e+18},
    {'symbol': 'P', 'name': 'peta', 'factor': 1e+15},
    {'symbol': 'T', 'name': 'tera', 'factor': 1e+12},
    {'symbol': 'G', 'name': 'giga', 'factor': 1e+9},
    {'symbol': 'M', 'name': 'mega', 'factor': 1e+6},
    {'symbol': 'k', 'name': 'kilo', 'factor': 1e+3},
    {'symbol': 'h', 'name': 'hecto', 'factor': 1e+2},
    {'symbol': 'da', 'name': 'deca', 'factor': 1e+1},
    {'symbol': '', 'name': '', 'factor': 1e0},
    {'symbol': ' ', 'name': None, 'factor': 0.0},
    {'symbol': 'd', 'name': 'deci', 'factor': 1e-1},
    {'symbol': 'c', 'name': 'centi', 'factor': 1e-2},
    {'symbol': 'm', 'name': 'milli', 'factor': 1e-3},
    {'symbol': 'μ', 'name': 'micro', 'factor': 1e-6},
    {'symbol': 'n', 'name': 'nano', 'factor': 1e-9},
    {'symbol': 'p', 'name': 'pico', 'factor': 1e-12},
    {'symbol': 'f', 'name': 'femto', 'factor': 1e-15},
    {'symbol': 'a', 'name': 'atto', 'factor': 1e-18},
    {'symbol': 'z', 'name': 'zepto', 'factor': 1e-21},
    {'symbol': 'y', 'name': 'yocto', 'factor': 1e-24},
]


UNITY = {'#', '1'}
"""Strings that represent dimensionless units."""


SYSTEMS = {'mks', 'cgs'}
"""The metric systems known to this module."""


_UNITS = [
    {
        'symbol': 'm',
        'name': 'meter',
        'quantity': 'length',
    },
    {
        'symbol': 'au',
        'name': 'astronomical unit',
        'quantity': 'length',
    },
    {
        'symbol': 'Rs',
        'name': 'solar radius',
        'quantity': 'length',
    },
    {
        'symbol': 'g',
        'name': 'gram',
        'quantity': 'mass',
    },
    {
        'symbol': 'nuc',
        'name': 'nucleon',
        'quantity': 'mass number',
    },
    {
        'symbol': 'amu',
        'name': 'atomic mass unit',
        'quantity': 'mass number',
    },
    {
        'symbol': 's',
        'name': 'second',
        'quantity': 'time',
    },
    {
        'symbol': 'min',
        'name': 'minute',
        'quantity': 'time',
    },
    {
        'symbol': 'h',
        'name': 'hour',
        'quantity': 'time',
    },
    {
        'symbol': 'd',
        'name': 'day',
        'quantity': 'time',
    },
    {
        'symbol': 'A',
        'name': 'ampere',
        'quantity': 'current',
    },
    {
        'symbol': 'K',
        'name': 'kelvin',
        'quantity': 'temperature',
    },
    {
        'symbol': 'mol',
        'name': 'mole',
        'quantity': 'amount',
    },
    {
        'symbol': '#',
        'name': 'count',
        'quantity': 'number',
    },
    {
        'symbol': 'cd',
        'name': 'candela',
        'quantity': 'luminous intensity',
    },
    {
        'symbol': 'rad',
        'name': 'radian',
        'quantity': 'plane angle',
    },
    {
        'symbol': 'deg',
        'name': 'degree',
        'quantity': 'plane angle',
    },
    {
        'symbol': 'sr',
        'name': 'steradian',
        'quantity': 'solid angle',
    },
    {
        'symbol': 'Hz',
        'name': 'hertz',
        'quantity': 'frequency',
    },
    {
        'symbol': 'J',
        'name': 'joule',
        'quantity': 'energy',
    },
    {
        'symbol': 'erg',
        'name': 'erg',
        'quantity': 'energy',
    },
    {
        'symbol': 'eV',
        'name': 'electronvolt',
        'quantity': 'energy',
    },
    {
        'symbol': 'N',
        'name': 'newton',
        'quantity': 'force',
    },
    {
        'symbol': 'dyn',
        'name': 'dyne',
        'quantity': 'force',
    },
    {
        'symbol': 'Pa',
        'name': 'pascal',
        'quantity': 'pressure',
    },
    {
        'symbol': 'W',
        'name': 'watt',
        'quantity': 'power',
    },
    {
        'symbol': 'C',
        'name': 'coulomb',
        'quantity': 'charge',
    },
    {
        'symbol': 'statC',
        'name': 'statcoulomb',
        'quantity': 'charge',
    },
    {
        'symbol': 'statA',
        'name': 'statampere',
        'quantity': 'current',
    },
    {
        'symbol': 'statV',
        'name': 'statvolt',
        'quantity': 'potential',
    },
    {
        'symbol': 'e',
        'name': 'fundamental charge',
        'quantity': 'charge',
    },
    {
        'symbol': 'V',
        'name': 'volt',
        'quantity': 'potential',
    },
    {
        'symbol': 'Ω',
        'name': 'ohm',
        'quantity': 'resistance',
    },
    {
        'symbol': 'S',
        'name': 'seimens',
        'quantity': 'conductance',
    },
    {
        'symbol': 'F',
        'name': 'farad',
        'quantity': 'capacitance',
    },
    {
        'symbol': 'Wb',
        'name': 'weber',
        'quantity': 'magnetic flux',
    },
    {
        'symbol': 'Mx',
        'name': 'maxwell',
        'quantity': 'magnetic flux',
    },
    {
        'symbol': 'Oe',
        'name': 'Oersted',
        'quantity': 'magnetic intensity',
    },
    {
        'symbol': 'H',
        'name': 'henry',
        'quantity': 'inductance',
    },
    {
        'symbol': 'T',
        'name': 'tesla',
        'quantity': 'magnetic induction',
    },
    {
        'symbol': 'G',
        'name': 'gauss',
        'quantity': 'magnetic induction',
    },
    {
        'symbol': 'lm',
        'name': 'lumen',
        'quantity': 'luminous flux',
    },
    {
        'symbol': 'lx',
        'name': 'lux',
        'quantity': 'illuminance',
    },
    {
        'symbol': 'Bq',
        'name': 'becquerel',
        'quantity': 'radioactivity',
    },
    {
        'symbol': 'Ci',
        'name': 'Curie',
        'quantity': 'radioactivity',
    },
    {
        'symbol': 'Gy',
        'name': 'gray',
        'quantity': 'dosage',
    },
    {
        'symbol': 'P',
        'name': 'poise',
        'quantity': 'viscosity',
    },
    {
        'symbol': '1',
        'name': 'unitless',
        'quantity': 'identity',
    },
]


def _build_named_units(
    prefixes: typing.List[typing.Dict[T, typing.Any]],
    units: typing.List[typing.Dict[T, str]],
) -> aliased.Mapping[T, typing.Dict[T, typing.Any]]:
    """Helper for building the collection of named units."""
    # Find the null metric prefix (0).
    null_prefix = next(
        prefix for prefix in prefixes if prefix['factor'] == 0.0
    )
    # Find the metric prefix corresponding to unity (1).
    base_prefix = next(
        prefix for prefix in prefixes if prefix['factor'] == 1.0
    )
    # Find the unitless quantity.
    unitless = next(
        unit for unit in units if unit['quantity'] == 'identity'
    )
    # Build mapping from (prefix, unit) combinations, as appropriate.
    mapped = {}
    for unit in units:
        if unit is unitless:
            # Prevent meaningless unitless expressions (e.g., cenitunitless).
            mapped[(unitless['symbol'], unitless['name'])] = {
                'prefix': base_prefix, 'base': unitless
            }
        else:
            for prefix in prefixes:
                if prefix is base_prefix:
                    # Add the unscaled unit.
                    mapped[(unit['symbol'], unit['name'])] = {
                        'prefix': base_prefix, 'base': unit
                    }
                elif prefix is not null_prefix:
                    # Add the full (prefix, unit) combination.
                    key = [
                        f"{prefix['symbol']}{unit['symbol']}",
                        f"{prefix['name']}{unit['name']}"
                    ]
                    if prefix['symbol'] == 'μ':
                        key += [f"u{unit['symbol']}"]
                    mapped[tuple(key)] = {'prefix': prefix, 'base': unit}
    return aliased.Mapping(mapped)


NAMED_UNITS = _build_named_units(_PREFIXES, _UNITS)


# A note about angles: Kalinin (2019) "On the status of plane and solid in the
# International System of Units (SI)" makes a very compelling argument that the
# plane- and solid-angle units should not be '1'; instead:
# - the plane-angle unit should be 'radian' ('rad'),
# - the solid-angle unit should be 'steradian' ('sr'), and
# - the plane angle should be a base quantity,
# - 'radian' should be considered a base unit,
# - 'steradian' should be considered a derived unit, with 'sr = rad^2'.

# References and notes on quantities, dimensions, and units:
# - https://en.wikipedia.org/wiki/International_System_of_Quantities#Base_quantities
# - https://www.nist.gov/pml/weights-and-measures/metric-si/si-units
# - This module uses 'H' to represent the dimension of temperature because the
#   SI character, $\Theta$, is not an ASCII character. I also considered 'O'
#   because of its similarity to $\Theta$, but it looks too much like '0'
#   (zero), which, ironically, looks more like $\Theta$ than 'O'.
# - This module adds an identity quantity with '1' as its dimension and unit

_BASE_QUANTITIES = container.Table(
    [
        {'name': 'identity', 'dimension': '1', 'unit': '1'},
        {'name': 'amount', 'dimension': 'N', 'unit': 'mol'},
        {'name': 'current', 'dimension': 'I', 'unit': 'A'},
        {'name': 'length', 'dimension': 'L', 'unit': 'm'},
        {'name': 'luminous intensity', 'dimension': 'J', 'unit': 'cd'},
        {'name': 'mass', 'dimension': 'M', 'unit': 'kg'},
        {'name': 'temperature', 'dimension': 'H', 'unit': 'K'},
        {'name': 'time', 'dimension': 'T', 'unit': 's'},
    ]
)

_QUANTITIES = {
    'acceleration': 'velocity / time',
    'amount': {
        'dimensions': {
            'mks': 'N',
            'cgs': 'N',
        },
        'units': {
            'mks': 'mol',
            'cgs': 'mol',
        },
    },
    'area': 'length^2',
    'capacitance': {
        'dimensions': {
            'mks': '(T^2 * I)^2 / (M * L^2)',
            'cgs': 'L',
        },
        'units': {
            'mks': 'F',
            'cgs': 'cm',
        },
    },
    'charge': {
        'dimensions': {
            'mks': 'I * T',
            'cgs': '(M^1/2 * L^3/2) / T',
        },
        'units': {
            'mks': 'C',
            'cgs': 'statC',
        },
    },
    'charge density': 'charge / volume',
    'conductance': {
        'dimensions': {
            'mks': '(T^3 * I^2) / (M * L^2)',
            'cgs': 'L / T',
        },
        'units': {
            'mks': 'S',
            'cgs': 'cm / s',
        },
    },
    'conductivity': 'conductance / length',
    'current': {
        'dimensions': {
            'mks': 'I',
            'cgs': '(M^1/2 * L^3/2) / T^2',
        },
        'units': {
            'mks': 'A',
            'cgs': 'statA',
        },
    },
    'current density': 'current / area',
    'displacement': {
        'dimensions': {
            'mks': 'I * T / L^2',
            'cgs': 'M^1/2 / (L^1/2 * T)',
        },
        'units': {
            'mks': 'C / m^2',
            'cgs': 'statC / m^2',
        },
    },
    'dosage': {
        'dimensions': {
            'mks': 'L^2 / T^2',
            'cgs': 'L^2 / T^2',
        },
        'units': {
            'mks': 'Gy',
            'cgs': 'erg / g', # Historically, 'rad', but that's in use.
        },
    },
    'electric charge': 'charge',
    'electric field': 'potential / length',
    'electromotance': 'potential',
    'energy': {
        'dimensions': {
            'mks': '(M * L^2) / T^2',
            'cgs': '(M * L^2) / T^2',
        },
        'units': {
            'mks': 'J',
            'cgs': 'erg',
        },
    },
    'energy density': 'energy / volume',
    'fluence': 'particle fluence',
    'flux': 'particle flux',
    'force': {
        'dimensions': {
            'mks': '(M * L) / T^2',
            'cgs': '(M * L) / T^2',
        },
        'units': {
            'mks': 'N',
            'cgs': 'dyn',
        },
    },
    'frequency': {
        'dimensions': {
            'mks': '1 / T',
            'cgs': '1 / T',
        },
        'units': {
            'mks': 'Hz',
            'cgs': 'Hz',
        },
    },
    'identity': {
        'dimensions': {
            'mks': '1',
            'cgs': '1',
        },
        'units': {
            'mks': '1',
            'cgs': '1',
        },
    },
    'illumunance': { # See note about radian (Kalinin 2019).
        'dimensions': {
            'mks': 'J / L^2',
            'cgs': 'J / L^2',
        },
        'units': {
            'mks': 'cd * sr / m^2',
            'cgs': 'cd * sr / cm^2',
        },
    },
    'impedance': {
        'dimensions': {
            'mks': '(M * L^2) / (T^3 * I)',
            'cgs': 'T / L',
        },
        'units': {
            'mks': 'ohm',
            'cgs': 's / cm',
        },
    },
    'inductance': {
        'dimensions': {
            'mks': '(M * L^2) / (I * T)^2',
            'cgs': 'T^2 / L',
        },
        'units': {
            'mks': 'H',
            'cgs': 's^2 / cm',
        },
    },
    'induction': 'magnetic induction',
    'integral flux': 'flux * energy',
    'length': {
        'dimensions': {
            'mks': 'L',
            'cgs': 'L',
        },
        'units': {
            'mks': 'm',
            'cgs': 'cm',
        },
    },
    'luminous flux': { # See note about radian (Kalinin 2019).
        'dimensions': {
            'mks': 'J',
            'cgs': 'J',
        },
        'units': {
            'mks': 'cd * sr',
            'cgs': 'cd * sr',
        },
    },
    'luminous intensity': {
        'dimensions': {
            'mks': 'J',
            'cgs': 'J',
        },
        'units': {
            'mks': 'cd',
            'cgs': 'cd',
        },
    },
    'magnetic field': 'magnetic induction',
    'magnetic flux': {
        'dimensions': {
            'mks': '(M * L^2) / (T^2 * I)',
            'cgs': '(M^1/2 * L^3/2) / T',
        },
        'units': {
            'mks': 'Wb',
            'cgs': 'Mx',
        },
    },
    'magnetic induction': {
        'dimensions': {
            'mks': 'M / (T^2 * I)',
            'cgs': 'M^1/2 / (L^1/2 * T)',
        },
        'units': {
            'mks': 'T',
            'cgs': 'G',
        },
    },
    'magnetic intensity': {
        'dimensions': {
            'mks': 'I / L',
            'cgs': 'M^1/2 / (L^1/2 * T)',
        },
        'units': {
            'mks': 'A / m',
            'cgs': 'Oe',
        },
    },
    'magnetic moment': {
        'dimensions': {
            'mks': 'I * L^2',
            'cgs': '(M^1/2 * L^5/2) / T',
        },
        'units': {
            'mks': 'A * m^2',
            'cgs': 'Oe * cm^3',
        },
    },
    'magnetization': 'magnetic intensity',
    'magnetomotance': 'current',
    'mass': {
        'dimensions': {
            'mks': 'M',
            'cgs': 'M',
        },
        'units': {
            'mks': 'kg',
            'cgs': 'g',
        },
    },
    'mass density': 'mass / volume',
    'mass number': 'number',
    'momentum': {
        'dimensions': {
            'mks': '(M * L) / T',
            'cgs': '(M * L) / T',
        },
        'units': {
            'mks': 'kg * m / s',
            'cgs': 'g * cm / s',
        },
    },
    'momentum density': 'momentum / volume',
    'number': 'identity',
    'number density': '1 / volume',
    'particle distribution': '1 / (length * velocity)^3',
    'particle fluence': 'number / (area * solid_angle * energy / mass_number)',
    'particle flux': 'fluence / time',
    'permeability': {
        'dimensions': {
            'mks': '(M * L) / (I * T)^2',
            'cgs': '1',
        },
        'units': {
            'mks': 'H / m',
            'cgs': '1',
        },
    },
    'permittivity': {
        'dimensions': {
            'mks': 'T^4 * I / (M * L^3)',
            'cgs': '1',
        },
        'units': {
            'mks': 'F / m',
            'cgs': '1',
        },
    },
    'plane angle': { # See note about radian (Kalinin 2019).
        'dimensions': {
            'mks': '1',
            'cgs': '1',
        },
        'units': {
            'mks': 'rad',
            'cgs': 'rad',
        },
    },
    'polarization': 'charge / area',
    'potential': {
        'dimensions': {
            'mks': '(M * L^2) / (T^3 * I)',
            'cgs': '(M^1/2 * L^1/2) / T',
        },
        'units': {
            'mks': 'V',
            'cgs': 'statV',
        },
    },
    'power': {
        'dimensions': {
            'mks': 'M * L^2 / T^3',
            'cgs': 'M * L^2 / T^3',
        },
        'units': {
            'mks': 'W',
            'cgs': 'erg / s',
        },
    },
    'power density': 'power / volume',
    'pressure': {
        'dimensions': {
            'mks': 'M / (L * T^2)',
            'cgs': 'M / (L * T^2)',
        },
        'units': {
            'mks': 'Pa',
            'cgs': 'dyn / cm^2', # also barye (Ba)?
        },
    },
    'radioactivity': {
        'dimensions': {
            'mks': '1 / T',
            'cgs': '1 / T',
        },
        'units': {
            'mks': 'Bq',
            'cgs': 'Ci',
        },
    },
    'rate': 'frequency',
    'ratio': 'identity',
    'reluctance': {
        'dimensions': {
            'mks': '(I * T)^2 / (M * L^2)',
            'cgs': '1 / L',
        },
        'units': {
            'mks': 'A / Wb',
            'cgs': '1 / cm',
        },
    },
    'resistance': 'impedance',
    'resistivity': 'resistance * length',
    'temperature': {
        'dimensions': {
            'mks': 'H',
            'cgs': 'H',
        },
        'units': {
            'mks': 'K',
            'cgs': 'K',
        },
    },
    'thermal conductivity': 'power / (length * temperature)',
    'time': {
        'dimensions': {
            'mks': 'T',
            'cgs': 'T',
        },
        'units': {
            'mks': 's',
            'cgs': 's',
        },
    },
    'solid angle': { # See note about radian (Kalinin 2019).
        'dimensions': {
            'mks': '1',
            'cgs': '1',
        },
        'units': {
            'mks': 'sr',
            'cgs': 'sr',
        },
    },
    'speed': 'velocity',
    'vector potential': {
        'dimensions': {
            'mks': '(M * L) / (T^2 * I)',
            'cgs': '(M^1/2 * L^1/2) / T',
        },
        'units': {
            'mks': 'Wb / m',
            'cgs': 'G * cm',
        },
    },
    'velocity': 'length / time',
    'viscosity': {
        'dimensions': {
            'mks': 'M / (L * T)',
            'cgs': 'M / (L * T)',
        },
        'units': {
            'mks': 'kg / (m * s)',
            'cgs': 'P',
        },
    },
    'volume': 'length^3',
    'vorticity': 'frequency',
    'wavenumber': '1 / length',
    'work': 'energy',
}


C = 2.99792458e10
"""The speed of light in cm/s."""
PI = numpy.pi
"""The ratio of a circle's circumference to its diameter."""


_CONVERSIONS = {
    ('Rs', 'm'): 6.96e8,
    ('F', 'cm'): C**2 * 1e-9,
    ('C', 'statC'): 10*C,
    ('e', 'C'): 1.6022e-19,
    ('S', 'cm / s'): C**2 * 1e-5,
    ('A', 'statA'): 10*C,
    # ('C / m^2', 'statC / m^2'): 4*PI * C * 1e-3,
    ('Gy', 'erg / g'): 1e4,
    ('J', 'erg'): 1e7,
    ('eV', 'J'): 1.6022e-19,
    ('N', 'dyn'): 1e5,
    ('ohm', 's / cm'): 1e5 / C**2,
    ('H', 's^2 / cm'): 1e5 / C**2,
    # ('m', 'cm'): 1e2,
    ('au', 'm'): 1.495978707e11,
    ('Wb', 'Mx'): 1e8,
    ('T', 'G'): 1e4,
    ('A / m', 'Oe'): 4*PI * 1e-3,
    # ('A * m^2', 'Oe * cm^3'): 1e-3,
    # ('kg', 'g'): 1e3,
    ('nuc', 'kg'): 1.6605e-27,
    ('amu', 'kg'): 1.6605e-27,
    # ('kg * m / s', 'g * cm / s'): 1e5,
    ('H / m', '1'): 1e7 / 4*PI,
    ('F / m', '1'): 36*PI * 1e9,
    ('rad', 'deg'): 180 / PI,
    ('V', 'statV'): 1e6 / C,
    ('W', 'erg / s'): 1e7,
    ('Pa', 'dyn / cm^2'): 1e1,
    ('Bq', 'Ci'): 1.0 / 3.7e10,
    ('A / Wb', '1 / cm'): 4*PI * 1e-9,
    ('s', 'min'): 1.0 / 60.0,
    ('s', 'h'): 1.0 / 3600.0,
    ('s', 'd'): 1.0 / 86400.0,
    ('Wb / m', 'G * cm'): 1e6,
    ('kg / (m * s)', 'P'): 1e1,
}


CONVERSIONS = container.Graph(_CONVERSIONS)


_NONSTANDARD = {
    'julian date': 'day',
    'shell': '1',
    'cos(mu)': '1',
    'e-': 'e',
    '# / cm^2 s sr MeV': '# / cm^2 s sr MeV/nuc',
}
"""Internal substitutions for non-standard EPREM units.

This dictionary maps each non-standard unit associated with an EPREM output
quantity to a unit defined in `~metric.py`.
"""

def standardize(unit: T):
    """Replace this unit string with a standard unit string, if possible.

    This function looks for `unit` in the known conversions and returns the
    standard unit string if it exists. If this doesn't find a standard unit
    string, it just returns the input.
    """
    unit = _NONSTANDARD.get(str(unit), unit)
    if '/' in unit:
        num, den = str(unit).split('/', maxsplit=1)
        unit = ' / '.join((num.strip(), f"({den.strip()})"))
    return unit

