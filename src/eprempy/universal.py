"""
Values and metadata of universal physical constants.
"""

import collections.abc
import typing

import numpy

from . import aliased
from . import measured
from . import physical
from . import real


_constants = {
    'pi': {
        'info': "The ratio of a circle's circumference to its diameter.",
        'all': numpy.pi,
        'quantity': 'number',
    },
    'k': {
        'info': "Boltzmann's constant.",
        'mks': {'unit': 'J / K', 'value': 1.3807e-23},
        'cgs': {'unit': 'erg / K', 'value': 1.3807e-16},
        'quantity': 'energy / temperature'
    },
    'e': {
        'info': "Elementary charge.",
        'mks': {'unit': 'C', 'value': 1.6022e-19},
        'cgs': {'unit': 'statC', 'value': 4.8032e-10},
        'quantity': 'charge',
    },
    'me': {
        'info': "Electron mass.",
        'mks': {'unit': 'kg', 'value': 9.1094e-31},
        'cgs': {'unit': 'g', 'value': 9.1094e-28},
        'quantity': 'mass',
    },
    'mp': {
        'info': "Proton mass.",
        'mks': {'unit': 'kg', 'value': 1.6726e-27},
        'cgs': {'unit': 'g', 'value': 1.6726e-24},
        'quantity': 'mass',
    },
    'G': {
        'info': "Gravitational constant.",
        'mks': {'unit': 'm^3 / (s^2 * kg)', 'value': 6.6726e-11},
        'cgs': {'unit': 'dyn * cm^2 / g^2', 'value': 6.6726e-8},
        'quantity': 'force * area / mass^2',
    },
    'g': {
        'info': "Gravitational acceleration.",
        'mks': {'unit': 'm / s^2', 'value': 9.8067},
        'cgs': {'unit': 'cm / s^2', 'value': 9.8067e2},
        'quantity': 'acceleration',
    },
    'h': {
        'info': "Planck's constant.",
        'mks': {'unit': 'J * s', 'value': 6.6261e-34},
        'cgs': {'unit': 'erg * s', 'value': 6.6261e-27},
        'quantity': 'energy * time',
    },
    'c': {
        'info': "Speed of light in a vacuum.",
        'mks': {'unit': 'm / s', 'value': 2.99792458e8},
        'cgs': {'unit': 'cm / s', 'value': 2.99792458e10},
        'quantity': 'speed',
    },
    'epsilon0': {
        'info': "Permittivity of free space.",
        'mks': {'unit': 'F / m', 'value': 8.8542e-12},
        'cgs': {'unit': '1', 'value': 1.0},
        'quantity': 'permittivity',
    },
    'mu0': {
        'info': "Permeability of free space.",
        'mks': {'unit': 'H / m', 'value': 4*numpy.pi * 1e-7},
        'cgs': {'unit': '1', 'value': 1.0},
        'quantity': 'permeability',
    },
    'Rinfinity': {
        'info': "Rydberg constant.",
        'mks': {'unit': '1 / m', 'value': 1.0974e7},
        'cgs': {'unit': '1 / cm', 'value': 1.0974e5},
        'quantity': '1 / length',
    },
    'a0': {
        'info': "Bohr radius.",
        'mks': {'unit': 'm', 'value': 5.2918e-11},
        'cgs': {'unit': 'cm', 'value': 5.2918e-9},
        'quantity': 'length',
    },
    're': {
        'info': "Classical electron radius.",
        'mks': {'unit': 'm', 'value': 2.8179e-15},
        'cgs': {'unit': 'cm', 'value': 2.8179e-13},
        'quantity': 'length',
    },
    'alpha': {
        'info': "Fine structure constant.",
        'mks': {'unit': '1', 'value': 7.2974e-3},
        'cgs': {'unit': '1', 'value': 7.2974e-3},
        'quantity': 'number',
    },
    'c1': {
        'info': "First radiation constant.",
        'mks': {'unit': 'W * m^2', 'value': 3.7418e-16},
        'cgs': {'unit': 'erg * cm^2 / s', 'value': 3.7418e-16},
        'quantity': 'power * area',
    },
    'c2': {
        'info': "Second radiation constant.",
        'mks': {'unit': 'm * K', 'value': 1.4388e-2},
        'cgs': {'unit': 'cm * K', 'value': 1.4388},
        'quantity': 'length * temperature',
    },
    'sigma': {
        'info': "Stefan-Boltzmann constant.",
        'mks': {'unit': 'W / (m^2 * K^4)', 'value': 5.6705e-8},
        'cgs': {'unit': '(erg / s) / (cm^2 * K^4)', 'value': 5.6705e-5},
        'quantity': 'power / (area * temperature^4)',
    },
    'eV': {
        'info': "Energy associated with 1 eV.",
        'mks': {'unit': 'J', 'value': 1.6022e-19},
        'cgs': {'unit': 'erg', 'value': 1.6022e-12},
        'quantity': 'energy',
    },
    'amu': {
        'info': "Atomic mass unit.",
        'mks': {'unit': 'kg', 'value': 1.6605e-27},
        'cgs': {'unit': 'g', 'value': 1.6605e-24},
        'quantity': 'mass',
    },
    'au': {
        'info': "Astronomical unit.",
        'mks': {'unit': 'm', 'value': 1.495978707e11},
        'cgs': {'unit': 'cm', 'value': 1.495978707e13},
        'quantity': 'length',
    },
}
_constants['H+'] = {
    'info': "First ionization energy of hydrogen.",
    **{
        k: {
            'unit': _constants['eV'][k]['unit'],
            'value': 13.6 * _constants['eV'][k]['value'],
        }
        for k in ('mks', 'cgs')
    },
    'quantity': 'energy',
}
_constants['MeV'] = {
    'info': _constants['eV']['info'].replace('eV', 'MeV'),
    **{
        k: {
            'unit': _constants['eV'][k]['unit'],
            'value': 1e6 * _constants['eV'][k]['value'],
        }
        for k in ('mks', 'cgs')
    },
    'quantity': 'energy',
}


def _normalize(
    defined: typing.Dict[str, typing.Dict[str, typing.Any]],
) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
    """Normalize constant definitions."""
    systems = ('mks', 'cgs')
    norm = {}
    for key, definition in defined.items():
        if 'all' in definition:
            value = definition.pop('all')
            new = {k: {'unit': '1', 'value': value} for k in systems}
            definition.update(new)
        norm[key] = definition
    return norm


# NOTE: I'm not sure that this needs to be an aliased mapping.
CONSTANTS = aliased.Mapping(_normalize(_constants))


class Constant(measured.Value[real.ValueType]):
    """A universal physical constant.
    
    An instance of this class represents the value of a named physical constant
    in a particular metric system, as well as the following metadata

    - the system-independent metric quantity
    - the system-specific metric unit, if applicable
    - a brief description
    """

    def __init__(
        self,
        value: measured.Value,
        /,
        quantity: str,
        info: str,
    ) -> None:
        """Called to initialize a constant object.
        
        It is usually not necessary to create instances of this class by hand.
        Please see `~Constants` for a mapping of universal physical constants
        with values and units in a given metric system.
        """
        super().__init__(value.data, value.context)
        self._quantity = quantity
        self._info = info

    @property
    def asscalar(self):
        """Extract the value and unit as a scalar object."""
        return physical.scalar(self.data, unit=self.unit)

    def __str__(self) -> str:
        base = super().__str__()
        extra = f"quantity={self.quantity!r}, info={self.info!r}"
        return f"{base}, {extra}"

    @property
    def quantity(self):
        """The corresponding metric quantity."""
        return self._quantity

    @property
    def info(self):
        """A brief description of this constant."""
        return self._info


class Constants(collections.abc.Mapping):
    """Universal physical constants in a given metric system."""
    def __init__(self, system: str) -> None:
        self.system = system.lower()
        self._mapping = CONSTANTS.copy()

    def __len__(self) -> int:
        """The number of defined constants."""
        return len(self._mapping)

    def __iter__(self) -> typing.Iterator:
        """Iterate over defined constants."""
        return iter(self._mapping)

    def __getitem__(self, name: str):
        """Create the named constant or raise an error."""
        try:
            definition = self._mapping[name]
        except KeyError as err:
            raise KeyError(f"Unknown constant: {name!r}") from err
        return self._create(definition)

    def _create(self, definition: dict):
        """Create a constant object from the given definition."""
        value = definition[self.system]['value']
        unit = definition[self.system]['unit']
        quantity = definition['quantity']
        info = definition['info']
        x = measured.value(value, unit=unit)
        return Constant(x, quantity, info)

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        return f"{self.__class__.__qualname__}({self.system})"


MKS = Constants('mks')
"""Fundamental constants in MKS unit where applicable."""

CGS = Constants('cgs')
"""Fundamental constants in cgs unit where applicable."""


def show():
    """Print all defined physical constants."""
    for key, data in CONSTANTS.items(aliased=True):
        print(f"{key}: {data['info']}")
        for system in ('mks', 'cgs'):
            value = data[system]['value']
            unit = data[system]['unit']
            base = f"{system}: {value}"
            line = f"{base} [{unit}]" if unit != '1' else base
            print(f"\t{line}")
        print()


if __name__ == '__main__':
    show()


