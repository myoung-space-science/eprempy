import pathlib
import typing

from eprempy import dataset


def test_arrays(
    datadir: pathlib.Path,
    datasets: typing.Dict[str, typing.Dict[str, str]],
    primary: typing.Dict[str, typing.Dict[str, dict]],
) -> None:
    """Test the interface to dataset array-like quantities."""
    systems = {'mks', 'cgs'}
    for rundir, data in datasets.items():
        current = primary[rundir]
        dimensions = {k: v['dimensions'] for k, v in current.items()}
        units = {
            s: {k: v['unit'][s] for k, v in current.items()}
            for s in systems
        }
        datapath = datadir / rundir / data['source']
        for system in systems:
            arrays = dataset.arrays(datapath, system=system)
            assert arrays.system == system
            check_arrays(arrays, dimensions, units[system])


def check_arrays(
    this: dataset.Arrays,
    dimensions: typing.Dict[str, typing.Tuple[str]],
    units: typing.Dict[str, str],
) -> None:
    """Helper for `test_arrays`."""
    assert this.time.dimensions == dimensions['time']
    assert this.time.unit == units['time']
    # - shell?
    # - species ?
    assert this.energy.dimensions == dimensions['energy'][1] # HACK
    assert this.energy.unit == units['energy']
    assert this.v.dimensions == dimensions['v'][1] # HACK
    assert this.v.unit == units['v']
    assert this.mu.dimensions == dimensions['mu']
    assert this.mu.unit == units['mu']
    assert this.mass.dimensions == dimensions['mass']
    assert this.mass.unit == units['mass']
    assert this.charge.dimensions == dimensions['charge']
    assert this.charge.unit == units['charge']
    assert this.r.dimensions == dimensions['r']
    assert this.r.unit == units['r']
    assert this.theta.dimensions == dimensions['theta']
    assert this.theta.unit == units['theta']
    assert this.phi.dimensions == dimensions['phi']
    assert this.phi.unit == units['phi']
    assert this.br.dimensions == dimensions['br']
    assert this.br.unit == units['br']
    assert this.btheta.dimensions == dimensions['btheta']
    assert this.btheta.unit == units['btheta']
    assert this.bphi.dimensions == dimensions['bphi']
    assert this.bphi.unit == units['bphi']
    assert this.ur.dimensions == dimensions['ur']
    assert this.ur.unit == units['ur']
    assert this.utheta.dimensions == dimensions['utheta']
    assert this.utheta.unit == units['utheta']
    assert this.uphi.dimensions == dimensions['uphi']
    assert this.uphi.unit == units['uphi']
    assert this.rho.dimensions == dimensions['rho']
    assert this.rho.unit == units['rho']
    assert this.hasdist or this.hasflux
    if this.hasflux:
        assert this.f is None
        assert this.flux.dimensions == dimensions['flux']
        assert this.flux.unit == units['flux']
    if this.hasdist:
        assert this.f.dimensions == dimensions['f']
        assert this.f.unit == units['f']
        assert this.flux is None

