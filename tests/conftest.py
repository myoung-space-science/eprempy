import pathlib
import typing

import numpy
import pytest

import support


@pytest.fixture(scope='package')
def measurables():
    """Implicitly measurable sequences."""

    unity = '1'
    unitless = [
        {'test': 1.1,    'full': (1.1, unity), 'dist': ((1.1, unity),)},
        {'test': (1.1,), 'full': (1.1, unity), 'dist': ((1.1, unity),)},
        {'test': [1.1],  'full': (1.1, unity), 'dist': ((1.1, unity),)},
        {
            'test': (1.1, 2.3),
            'full': (1.1, 2.3, unity),
            'dist': ((1.1, unity), (2.3, unity)),
        },
        {
            'test': [1.1, 2.3],
            'full': (1.1, 2.3, unity),
            'dist': ((1.1, unity), (2.3, unity)),
        },
    ]
    meter = 'm'
    withunit = [
        {'test': (1.1, meter), 'full': (1.1, meter), 'dist': ((1.1, meter),)},
        {'test': [1.1, meter], 'full': (1.1, meter), 'dist': ((1.1, meter),)},
        {
            'test': (1.1, 2.3, meter),
            'full': (1.1, 2.3, meter),
            'dist': ((1.1, meter), (2.3, meter))
        },
        {
            'test': [1.1, 2.3, meter],
            'full': (1.1, 2.3, meter),
            'dist': ((1.1, meter), (2.3, meter)),
        },
        {
            'test': [(1.1, 2.3), meter],
            'full': (1.1, 2.3, meter),
            'dist': ((1.1, meter), (2.3, meter)),
        },
        {
            'test': [[1.1, 2.3], meter],
            'full': (1.1, 2.3, meter),
            'dist': ((1.1, meter), (2.3, meter)),
        },
        {
            'test': ((1.1, meter), (2.3, meter)),
            'full': (1.1, 2.3, meter),
            'dist': ((1.1, meter), (2.3, meter)),
        },
        {
            'test': [(1.1, meter), (2.3, meter)],
            'full': (1.1, 2.3, meter),
            'dist': ((1.1, meter), (2.3, meter)),
        },
        {
            'test': [(1.1, meter), (2.3, 5.8, meter)],
            'full': (1.1, 2.3, 5.8, meter),
            'dist': ((1.1, meter), (2.3, meter), (5.8, meter)),
        },
    ]
    return [
        *unitless,
        *withunit,
    ]


@pytest.fixture
def ndarrays():
    """Base `numpy` arrays for tests."""
    r = [ # (3, 2)
        [+1.0, +2.0],
        [+2.0, -3.0],
        [-4.0, +6.0],
    ]
    xy = [ # (3, 2)
        [+10.0, +20.0],
        [-20.0, -30.0],
        [+40.0, +60.0],
    ]
    yz = [ # (2, 4)
        [+4.0, -4.0, +4.0, -4.0],
        [-6.0, +6.0, -6.0, +6.0],
    ]
    zw = [ # (4, 5)
        [+1.0, +2.0, +3.0, +4.0, +5.0],
        [-1.0, -2.0, -3.0, -4.0, -5.0],
        [+5.0, +4.0, +3.0, +2.0, +1.0],
        [-5.0, -4.0, -3.0, -2.0, -1.0],
    ]
    xyz = [ # (3, 2, 4)
        [
            [+4.0, -4.0, +4.0, -4.0],
            [-6.0, +6.0, -6.0, +6.0],
        ],
        [
            [+16.0, -16.0, +4.0, -4.0],
            [-6.0, +6.0, -18.0, +18.0],
        ],
        [
            [-4.0, +4.0, -4.0, +4.0],
            [+6.0, -6.0, +6.0, -6.0],
        ],
    ]
    return support.NDArrays(
        r=numpy.array(r),
        xy=numpy.array(xy),
        yz=numpy.array(yz),
        zw=numpy.array(zw),
        xyz=numpy.array(xyz),
    )


@pytest.fixture
def rootpath():
    """The path containing `tests` and `data` directories."""
    cwd = pathlib.Path(__file__).expanduser().resolve()
    return cwd.parent


@pytest.fixture
def datadir(rootpath: pathlib.Path):
    """The top-level directory containing test data."""
    return rootpath / 'data'


@pytest.fixture
def datasets():
    """A collection of dataset directory attributes."""
    return {
        'isotropic-shock-with-flux': {
            'source': 'flux000000.nc',
            'config': 'eprem.cfg',
        },
        'wind-with-flux': {
            'source': 'flux000000.nc',
            'config': 'eprem.cfg',
        },
        'isotropic-shock-with-dist': {
            'source': 'obs000000.nc',
            'config': 'eprem.cfg',
        },
        'wind-with-dist': {
            'source': 'obs000000.nc',
            'config': 'eprem.cfg',
        },
    }


@pytest.fixture
def config(
    datadir: pathlib.Path,
    datasets: typing.Dict[str, typing.Dict[str, str]]
) -> None:
    """Parameter values corresponding to each test dataset."""
    common = {
        'numRowsPerFace': 3,
        'numColumnsPerFace': 3,
        'numNodesPerStream': 1000,
        'numEnergySteps': 30,
        'numMuSteps': 11,
        'rScale': 0.0046524726370988385,
        'simStartTime': 0.0,
        'simStopTime': 5.0,
        'tDel': 0.1,
        'eMin': 0.1,
        'eMax': 100.0,
        'lamo': 1.0,
        'mfpRadialPower': 0.666666666666667,
        'kperxkpar': 0.01,
        'boundaryFunctAmplitude': 100.0,
        'boundaryFunctXi': 1.0,
        'boundaryFunctGamma': 2.0,
        'boundaryFunctBeta': 1.7,
        'boundaryFunctEcutoff': 1.0,
        'flowMag': 300.0e5,
        'mhdDensityAu': 8.30,
        'mhdBAu': 1.60e-5,
        'numSpecies': 1,
        'mass': [1.0],
        'charge': [1.0],
        'useDrift': 0,
        'useShellDiffusion': 0,
        'unifiedOutput': 1,
        'epremDomain': 0,
        'dumpFreq': 1,
        'numObservers': 0,
        'idw_p': 3.0,
        'numEpSteps': 30,
        'useParallelDiffusion': 1,
        'useAdiabaticChange': 1,
        'useAdiabaticFocus': 1,
        'gammaElow': 0.0,
        'gammaEhigh': 0.0,
        'boundaryFunctionInitDomain': 1,
        'checkSeedPopulation': 1,
        'omegaSun': 0.001429813,
        'subTimeCouple': 0,
        'FailModeDump': 1,
    }
    shock_on = {
        'idealShock': 1,
        'idealShockSharpness': 1.0,
        'idealShockScaleLength': 0.001,
        'idealShockJump': 4.0,
        'idealShockSpeed': 1000.0e5,
        'idealShockInitTime': 0.5,
        'idealShockWidth': 0.0,
        'idealShockFalloff': 0.0,
    }
    shock_dist = {**common, **shock_on, 'streamFluxOutput': 0}
    shock_flux = {**common, **shock_on, 'streamFluxOutput': 1}
    wind_dist = {**common, 'idealShock': 0, 'streamFluxOutput': 0}
    wind_flux = {**common, 'idealShock': 0, 'streamFluxOutput': 1}
    built = {
        'isotropic-shock-with-dist': {'args': shock_dist},
        'isotropic-shock-with-flux': {'args': shock_flux},
        'wind-with-dist': {'args': wind_dist},
        'wind-with-flux': {'args': wind_flux},
    }
    for k, v in built.items():
        v['path'] = (datadir / k / datasets[k]['config'])
    return built


T, S, P, E, M = 'time', 'shell', 'species', 'energy', 'mu'


@pytest.fixture
def primary():
    """The primary observable quantities."""
    common = {
        'time': {
            'unit': {'mks': 's', 'cgs': 's'},
            'dimensions': (T,),
            'aliases': ['t', 'times'],
        },
        'shell': {
            'unit': {'mks': '1', 'cgs': '1'},
            'dimensions': (S,),
            'aliases': ['shells'],
        },
        'mu': {
            'unit': {'mks': '1', 'cgs': '1'},
            'dimensions': (M,),
            'aliases': [
                'mu',
                'pitch angle', 'pitch-angle', 'pitch-angle cosine',
                'pitch angles', 'pitch-angles', 'pitch-angle cosines',
            ],
        },
        'phiOffset': {
            'unit': {'mks': 's', 'cgs': 's'},
            'dimensions': (T,),
            'aliases': [],
        },
        'mass': {
            'unit': {'mks': 'kg', 'cgs': 'g'},
            'dimensions': (P,),
            'aliases': ['m'],
        },
        'charge': {
            'unit': {'mks': 'C', 'cgs': 'statC'},
            'dimensions': (P,),
            'aliases': ['q'],
        },
        'energy': {
            'unit': {'mks': 'J', 'cgs': 'erg'},
            'dimensions': (P, E),
            'aliases': ['energies', 'E'],
        },
        'v': {
            'unit': {'mks': 'm / s', 'cgs': 'cm / s'},
            'dimensions': (P, E),
            'aliases': ['speed'],
        },
        'r': {
            'unit': {'mks': 'm', 'cgs': 'cm'},
            'dimensions': (T, S),
            'aliases': ['radius'],
        },
        'theta': {
            'unit': {'mks': 'rad', 'cgs': 'rad'},
            'dimensions': (T, S),
            'aliases': [],
        },
        'phi': {
            'unit': {'mks': 'rad', 'cgs': 'rad'},
            'dimensions': (T, S),
            'aliases': [],
        },
        'br': {
            'unit': {'mks': 'T', 'cgs': 'G'},
            'dimensions': (T, S),
            'aliases': ['Br'],
        },
        'btheta': {
            'unit': {'mks': 'T', 'cgs': 'G'},
            'dimensions': (T, S),
            'aliases': ['bt', 'Btheta', 'Bt'],
        },
        'bphi': {
            'unit': {'mks': 'T', 'cgs': 'G'},
            'dimensions': (T, S),
            'aliases': ['bp', 'Bphi', 'Bp'],
        },
        'ur': {
            'unit': {'mks': 'm / s', 'cgs': 'cm / s'},
            'dimensions': (T, S),
            'aliases': ['Ur', 'Vr', 'vr'],
        },
        'utheta': {
            'unit': {'mks': 'm / s', 'cgs': 'cm / s'},
            'dimensions': (T, S),
            'aliases': ['ut', 'Utheta', 'Ut', 'Vtheta', 'Vt'],
        },
        'uphi': {
            'unit': {'mks': 'm / s', 'cgs': 'cm / s'},
            'dimensions': (T, S),
            'aliases': ['up', 'Uphi', 'Up', 'Vphi', 'Vp'],
        },
        'rho': {
            'unit': {'mks': 'm^-3', 'cgs': 'cm^-3'},
            'dimensions': (T, S),
            'aliases': ['Rho'],
        },
    }
    dist = common.copy()
    dist['f'] = {
        'unit': {'mks': 's^3 / m^6', 'cgs': 's^3 / cm^6'},
        'dimensions': (T, S, P, E, M),
        'aliases': ['dist', 'Dist'],
    }
    flux = common.copy()
    flux['flux'] = {
        'unit': {
            'mks': 'm^-2 s^-1 sr^-1 J^-1',
            'cgs': 'cm^-2 s^-1 sr^-1 erg^-1',
        },
        'dimensions': (T, S, P, E),
        'aliases': ['Flux', 'J', 'J(E)', 'j', 'j(E)'],
    }
    return {
        'isotropic-shock-with-dist': dist,
        'isotropic-shock-with-flux': flux,
        'wind-with-dist': dist,
        'wind-with-flux': flux,
    }


@pytest.fixture
def derived(
    primary: typing.Dict[str, typing.Dict[str, typing.Dict[str, typing.Any]]],
) -> typing.Dict[str, typing.Dict[str, typing.Dict[str, typing.Any]]]:
    """The derived observable quantities."""
    default = {
        'x': {
            'unit': {'mks': 'm', 'cgs': 'cm'},
            'dimensions': (T, S),
            'aliases': ['X'],
        },
        'y': {
            'unit': {'mks': 'm', 'cgs': 'cm'},
            'dimensions': (T, S),
            'aliases': ['Y'],
        },
        'z': {
            'unit': {'mks': 'm', 'cgs': 'cm'},
            'dimensions': (T, S),
            'aliases': ['Z'],
        },
        'bmag': {
            'unit': {'mks': 'T', 'cgs': 'G'},
            'dimensions': (T, S),
            'aliases': ['B', 'b', '|B|', '|b|', 'b_mag', 'b mag'],
        },
        'umag': {
            'unit': {'mks': 'm / s', 'cgs': 'cm / s'},
            'dimensions': (T, S),
            'aliases': ['U', 'u', '|U|', '|u|', 'u_mag', 'u mag'],
        },
        'upara': {
            'unit': {'mks': 'm / s', 'cgs': 'cm / s'},
            'dimensions': (T, S),
            'aliases': ['Upara', 'u_para'],
        },
        'uperp': {
            'unit': {'mks': 'm / s', 'cgs': 'cm / s'},
            'dimensions': (T, S),
            'aliases': ['Uperp', 'u_perp'],
        },
        'angle': {
            'unit': {'mks': 'rad', 'cgs': 'rad'},
            'dimensions': (T, S),
            'aliases': ['flow_angle', 'flow angle'],
        },
        'divu': {
            'unit': {'mks': '1 / s', 'cgs': '1 / s'},
            'dimensions': (T, S),
            'aliases': ['div_u', 'divU', 'div U', 'div u', 'div(U)', 'div(u)'],
        },
        'density_ratio': {
            'unit': {'mks': 'kg / m^3', 'cgs': 'g / cm^3'},
            'dimensions': (T, S),
            'aliases': ['density ratio' ,'n2/n1', 'n_2/n_1'],
        },
        'rigidity': {
            'unit': {'mks': 'kg m / (A s^2)', 'cgs': 'g cm / (statA s^2)'},
            'dimensions': (P, E),
            'aliases': ['Rg', 'R_g'],
        },
        'mfp': {
            'unit': {'mks': 'm', 'cgs': 'cm'},
            'dimensions': (T, S, P, E),
            'aliases': ['mean_free_path', 'mean free path'],
        },
        'ar': {
            'unit': {'mks': '1 / s', 'cgs': '1 / s'},
            'dimensions': (T, S, P, E),
            'aliases': ['acceleration_rate', 'acceleration rate'],
        },
        'energy_density': {
            'unit': {'mks': 'J / m^3', 'cgs': 'erg / cm^3'},
            'dimensions': (T, S, P),
            'aliases': ['energy density'],
        },
        'average_energy': {
            'unit': {'mks': 'J', 'cgs': 'erg'},
            'dimensions': (T, S, P),
            'aliases': ['average energy'],
        },
        'fluence': {
            'unit': {'mks': '# / (m^2 sr J)', 'cgs': '# / (cm^2 sr erg)'},
            'dimensions': (T, S, P, E),
            'aliases': [],
        },
        'intflux': {
            'unit': {'mks': '# / (m^2 s sr)', 'cgs': '# / (cm^2 s sr)'},
            'dimensions': (T, S, P, 'minimum energy'),
            'aliases': ['integral_flux', 'integral flux'],
        },
    }
    obsdist = default.copy()
    obsdist['flux'] = primary['isotropic-shock-with-flux']['flux'].copy()
    return {
        'isotropic-shock-with-dist': obsdist,
        'isotropic-shock-with-flux': default,
        'wind-with-dist': obsdist,
        'wind-with-flux': default,
    }


@pytest.fixture
def observables(primary, derived):
    """All observable quantities."""
    excluded = {
        'shell',
        'phiOffset',
        'egrid',
        'vgrid',
    }
    name = 'isotropic-shock-with-dist'
    merged = {**primary[name], **derived[name]}
    return {k: v for k, v in merged.items() if k not in excluded}

