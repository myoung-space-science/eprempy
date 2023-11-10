import typing
import pathlib

import pytest

from eprempy import dataset
from eprempy import metric
from eprempy import observable
from eprempy import physical


def test_quantity_unit_conversion():
    """Test the ability to change a quantity's unit."""
    context = None
    dimensions = ['x']
    old = metric.unit('cm / s')
    new = metric.unit('au / h')
    q = observable.Quantity(context, unit=old, dimensions=dimensions)
    w = observable.Quantity(context, unit=new, dimensions=dimensions)
    assert q.withunit(new) == w
    assert q.withunit(old) is q
    with pytest.raises(ValueError):
        q.withunit('J')


class Wrapper:
    """Helper for testing observable quantities."""

    def __init__(
        self,
        observables: typing.Dict[str, typing.Any],
        datadir: pathlib.Path,
        datasets: typing.Dict[str, typing.Dict[str, str]],
    ) -> None:
        self.observables = observables
        self.datadir = datadir
        self.datasets = datasets
        self.user = {
            'time': slice(1, 5),
            'shell': slice(1, 6),
            'species': slice(0, 1),
            'energy': slice(1, 4),
            'mu': slice(1, 3),
            'minimum energy': [1.0, 5.0, 'MeV'],
            'radius': [0.5, 'au'],
            'radii': [0.1, 0.5, 'au'],
        }

    def check(self, name: str) -> None:
        """Helper for tests of observable quantities."""
        for rundir, data in self.datasets.items():
            source = self.datadir / rundir / data['source']
            config = self.datadir / rundir / data['config']
            self._check(name, source, config)

    def _check(self, name: str, source: pathlib.Path, config: pathlib.Path):
        expected = self.observables[name]
        dataview = dataset.view(source)
        dimensions = list(expected['dimensions'])
        sizes = [
            dataview.axes[k].size for k in dimensions
            if k in dataview.axes
        ]
        if 'minimum energy' in dimensions:
            sizes.append(dataview.axes['energy'].size)
        indices = [self.user[k] for k in dimensions]
        arrays = observable.quantities(source, config)
        if name == 'f' and arrays.dataset.hasflux:
            return
        result = arrays[name]
        assert isinstance(result, observable.Quantity)
        assert result.dimensions == tuple(dimensions)
        assert result.unit & expected['unit'][str(arrays.system)]
        full = result[:]
        assert isinstance(full, physical.Array)
        assert full.shape == tuple(sizes)
        assert full.unit == result.unit
        partial = result[tuple(indices)]
        assert isinstance(partial, physical.Array)
        shape = [
            s.stop - s.start if isinstance(s, slice) else len(s[:-1])
            for s in indices
        ]
        assert partial.shape == tuple(shape)
        assert partial.unit == result.unit
        idx = [
            s.start if isinstance(s, slice) else [s[0], s[-1]]
            for s in indices
        ]
        singlular = result[tuple(idx)]
        assert isinstance(singlular, physical.Array)
        assert singlular.unit == result.unit
        if 'shell' in dimensions:
            for key in 'radius', 'radii':
                r = self.user[key]
                interpolated = result[:, r, ...]
                shape = [
                    len(r)-1 if k == 'shell' else v
                    for k, v in full.shapemap.items()
                ]
                assert isinstance(interpolated, physical.Array)
                assert interpolated.shape == tuple(shape)


@pytest.fixture
def wrapper(
    datadir: pathlib.Path,
    datasets: typing.Dict[str, typing.Dict[str, str]],
    observables: typing.Dict[str, typing.Dict[str, dict]],
) -> Wrapper:
    """An instance of the test-wrapper class."""
    return Wrapper(observables, datadir, datasets)


def test_r(wrapper: Wrapper):
    """Test the observable radial coordinate."""
    wrapper.check('r')


def test_theta(wrapper: Wrapper):
    """Test the observable polar coordinate."""
    wrapper.check('theta')


def test_phi(wrapper: Wrapper):
    """Test the observable azimuthal coordinate."""
    wrapper.check('phi')


def test_br(wrapper: Wrapper):
    """Test the observable magnetic-field radial component."""
    wrapper.check('br')


def test_btheta(wrapper: Wrapper):
    """Test the observable magnetic-field polar component."""
    wrapper.check('btheta')


def test_bphi(wrapper: Wrapper):
    """Test the observable magnetic-field azimuthal component."""
    wrapper.check('bphi')


def test_ur(wrapper: Wrapper):
    """Test the observable magnetic-field radial component."""
    wrapper.check('ur')


def test_utheta(wrapper: Wrapper):
    """Test the observable magnetic-field polar component."""
    wrapper.check('utheta')


def test_uphi(wrapper: Wrapper):
    """Test the observable magnetic-field azimuthal component."""
    wrapper.check('uphi')


def test_rho(wrapper: Wrapper):
    """Test the observable density."""
    wrapper.check('rho')


def test_f(wrapper: Wrapper):
    """Test the observable particle distribution."""
    wrapper.check('f')


def test_x(wrapper: Wrapper):
    """Test the observable x coordinate."""
    wrapper.check('x')


def test_y(wrapper: Wrapper):
    """Test the observable y coordinate."""
    wrapper.check('y')


def test_z(wrapper: Wrapper):
    """Test the observable z coordinate."""
    wrapper.check('z')


def test_bmag(wrapper: Wrapper):
    """Test the observable magnetic-field amplitude."""
    wrapper.check('bmag')


def test_umag(wrapper: Wrapper):
    """Test the observable velocity-field amplitude."""
    wrapper.check('umag')


def test_angle(wrapper: Wrapper):
    """Test the observable flow angle."""
    wrapper.check('angle')


def test_upara(wrapper: Wrapper):
    """Test the observable velocity-field component parallel to B."""
    wrapper.check('upara')


def test_uperp(wrapper: Wrapper):
    """Test the observable velocity-field component perpendicular to B."""
    wrapper.check('uperp')


def test_divu(wrapper: Wrapper):
    """Test the observable velocity-field divergence."""
    wrapper.check('divu')


def test_rigidity(wrapper: Wrapper):
    """Test the observable particle rigidity."""
    wrapper.check('rigidity')


def test_mfp(wrapper: Wrapper):
    """Test the observable mean free path."""
    wrapper.check('mfp')


def test_ar(wrapper: Wrapper):
    """Test the observable acceleration rate."""
    wrapper.check('ar')


def test_energy_density(wrapper: Wrapper) -> None:
    """Test the observable energy density."""
    wrapper.check('energy_density')


def test_average_energy(wrapper: Wrapper) -> None:
    """Test the observable average energy."""
    wrapper.check('average_energy')


def test_flux(wrapper: Wrapper) -> None:
    """Test the observable flux."""
    wrapper.check('flux')


def test_fluence(wrapper: Wrapper) -> None:
    """Test the observable fluence."""
    wrapper.check('fluence')


def test_intflux(wrapper: Wrapper) -> None:
    """Test the observable integral flux."""
    wrapper.check('intflux')



