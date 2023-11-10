import pathlib
import typing

import numpy

from eprempy import dataset


def test_view_factory(
    datadir: pathlib.Path,
    datasets: typing.Dict[str, typing.Dict[str, str]],
) -> None:
    """Test the ability to create format-agnostic views of a dataset."""
    cases = {
        'isotropic-shock-with-dist': {
            'arrays': set(dataset.ARRAYS) - {'flux'},
            'scalars': dataset.SCALARS,
            'axes': dataset.AXES,
        },
        'isotropic-shock-with-flux': {
            'arrays': set(dataset.ARRAYS) - {'Dist'},
            'scalars': dataset.SCALARS,
            'axes': dataset.AXES,
        },
    }
    for rundir, these in cases.items():
        data = datasets[rundir]
        current = dataset.view(datadir / rundir / data['source'])
        for name in these['arrays']:
            assert name in current.arrays
        for name in these['scalars']:
            assert name in current.scalars
        for name in these['axes']:
            assert name in current.axes


def test_egrid_shape(datadir: pathlib.Path):
    """Test the ability to detect 1D or 2D `egrid` in the dataset.

    This test exists because we changed `egrid` to be 1D (indexed only by
    species) in April 2023. It had previously been logically 2D (indexed by
    species and energy) but the energy dimension was always singular, making it
    effectively 1D.
    """
    old = dataset.view(datadir / 'misc' / 'egrid-2d.nc')
    new = dataset.view(datadir / 'misc' / 'egrid-1d.nc')
    assert old.axes['energy'].size == new.axes['energy'].size
    for current, ndim in zip((old, new), (2, 1)):
        assert numpy.array(current.arrays['egrid'].data).ndim == ndim


