"""
Metadata for EPREM objects.
"""

import typing

from . import aliased
from . import datafile
from . import metric


_metadata = {
    'phiOffset': {
        'quantity': 'plane angle',
        'aliases': [],
    },
    'time': {
        'quantity': 'time',
        'aliases': ['t', 'times'],
    },
    'shell': {
        'quantity': 'number',
        'aliases': ['shells'],
    },
    'mu': {
        'quantity': 'ratio',
        'aliases': [
            'mu',
            'pitch angle', 'pitch-angle', 'pitch-angle cosine',
            'pitch angles', 'pitch-angles', 'pitch-angle cosines',
        ],
    },
    'mass': {
        'quantity': 'mass',
        'aliases': ['m'],
    },
    'charge': {
        'quantity': 'charge',
        'aliases': ['q'],
    },
    'energy': {
        'quantity': 'energy',
        'aliases': ['energies', 'E', 'egrid'],
    },
    'v': {
        'quantity': 'velocity',
        'aliases': ['speed', 'vgrid'],
    },
    'r': {
        'quantity': 'length',
        'aliases': ['radius', 'R'],
    },
    'theta': {
        'quantity': 'plane angle',
        'aliases': ['T'],
    },
    'phi': {
        'quantity': 'plane angle',
        'aliases': ['P'],
    },
    'br': {
        'quantity': 'magnetic field',
        'aliases': ['Br'],
    },
    'btheta': {
        'quantity': 'magnetic field',
        'aliases': ['bt', 'Btheta', 'Bt'],
    },
    'bphi': {
        'quantity': 'magnetic field',
        'aliases': ['bp', 'Bphi', 'Bp'],
    },
    'ur': {
        'quantity': 'velocity',
        'aliases': ['Ur', 'Vr', 'vr'],
    },
    'utheta': {
        'quantity': 'velocity',
        'aliases': ['ut', 'Utheta', 'Ut', 'Vtheta', 'Vt'],
    },
    'uphi': {
        'quantity': 'velocity',
        'aliases': ['up', 'Uphi', 'Up', 'Vphi', 'Vp'],
    },
    'rho': {
        'quantity': 'number density',
        'aliases': ['Rho'],
    },
    'f': {
        'quantity': 'particle distribution',
        'aliases': ['dist', 'Dist'],
    },
    'flux': {
        'quantity': 'number / (area * solid_angle * time * energy)',
        'aliases': ['Flux', 'J', 'J(E)', 'j', 'j(E)'],
    },
    'x': {
        'quantity': 'length',
        'aliases': ['X'],
    },
    'y': {
        'quantity': 'length',
        'aliases': ['Y'],
    },
    'z': {
        'quantity': 'length',
        'aliases': ['Z'],
    },
    'bmag': {
        'quantity': 'magnetic field',
        'aliases': ['B', 'b', '|B|', '|b|', 'b_mag', 'b mag'],
    },
    'umag': {
        'quantity': 'velocity',
        'aliases': ['U', 'u', '|U|', '|u|', 'u_mag', 'u mag'],
    },
    'upara': {
        'quantity': 'velocity',
        'aliases': ['Upara', 'u_para'],
    },
    'uperp': {
        'quantity': 'velocity',
        'aliases': ['Uperp', 'u_perp'],
    },
    'angle': {
        'quantity': 'plane angle',
        'aliases': ['flow_angle', 'flow angle'],
    },
    'divu': {
        'quantity': '1 / time',
        'aliases': ['div_u', 'divU', 'div U', 'div u', 'div(U)', 'div(u)'],
    },
    'rigidity': {
        'quantity': 'momentum / charge',
        'aliases': ['Rg', 'R_g'],
    },
    'mfp': {
        'quantity': 'length',
        'aliases': ['mean_free_path', 'mean free path'],
    },
    'ar': {
        'quantity': '1 / time',
        'aliases': ['acceleration_rate', 'acceleration rate'],
    },
    'energy_density': {
        'quantity': 'energy / volume',
        'aliases': ['energy density'],
    },
    'average_energy': {
        'quantity': 'energy',
        'aliases': ['average energy'],
    },
    'fluence': {
        'quantity': 'number / (area * solid_angle * energy / mass_number)',
        'aliases': [],
    },
    'intflux': {
        'quantity': 'number / (area * solid_angle * time)',
        'aliases': ['integral_flux', 'integral flux'],
    },
}


_quantities = {
    (k, *v.get('aliases', [])): v['quantity']
    for k, v in _metadata.items()
}
QUANTITIES = aliased.Mapping(_quantities)
"""An aliased mapping from simulated quantity to physical quantity."""


ALIASES = aliased.Groups(*QUANTITIES.keys(aliased=True))
"""The defined alias(es) for each simulated quantity."""


class Subset(typing.NamedTuple):
    """Reference information for a subset of EPREM quantities."""
    aliases: aliased.Groups
    """The defined alias(es) for each member."""
    names: aliased.NameMap
    """A mapping from alias(es) to canonical name for each member."""


_SUBSETS = {
    'arrays': datafile.ARRAYS,
    'scalars': datafile.SCALARS,
    'axes': datafile.AXES,
    'observables': tuple(_metadata),
}


def build(*names, subset: str=None):
    """Build reference information for EPREM quantities."""
    keys = _SUBSETS.get(subset, names)
    aliases = aliased.Groups(*[ALIASES.get(key, [key]) for key in keys])
    namemap = aliased.NameMap({key: ALIASES.get(key, [key]) for key in keys})
    return Subset(aliases=aliases, names=namemap)


ARRAYS = build(subset='arrays')
"""Reference information for EPREM arrays."""


SCALARS = build(subset='scalars')
"""Reference information for EPREM scalars."""


AXES = build(subset='axes')
"""Reference information for EPREM axes."""


OBSERVABLES = build(subset='observables')
"""Reference information for EPREM observables."""


_units = {
    k: metric.UNITS[q]
    for k, q in QUANTITIES.items(aliased=True)
}

UNITS = aliased.Mapping(_units)
"""The unit of each observable quantity.

This mapping is keyed by quantity alias, then by metric system.

See Also
--------
`~metric.UNITS`
"""


_dimensions = {
    k: metric.DIMENSIONS[q]
    for k, q in QUANTITIES.items(aliased=True)
}

DIMENSIONS = aliased.Mapping(_dimensions)
"""The dimension of each observable quantity.

This mapping is keyed by quantity alias, then by metric system.

See Also
--------
`~metric.UNITS`
"""

