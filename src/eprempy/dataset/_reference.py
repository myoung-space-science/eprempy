"""
Names of quantities in an arbitrary EPREM dataset.
"""


ARRAYS = (
    'phiOffset',
    'time',
    'shell',
    'mu',
    'mass',
    'charge',
    'egrid',
    'vgrid',
    'R',
    'T',
    'P',
    'Br',
    'Bt',
    'Bp',
    'Vr',
    'Vt',
    'Vp',
    'Rho',
    'Dist',
    'flux',
)
"""The canonical names of array-like dataset quantities.

Note that not every named quantity will appear in each dataset. For example,
datasets generated by a run with `streamFluxOutput=1` will include 'flux' but
not 'Dist', while datasets generated by a run with `streamFluxOutput=0` will
include 'Dist' but not 'flux'.
"""


SCALARS = (
    'preEruption',
)
"""The canonical names of scalar dataset quantities."""


AXES = (
    'time',
    'shell',
    'species',
    'energy',
    'mu',
)
"""The canonical names of dataset axes."""


