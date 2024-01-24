"""
Configuration file for the `test_parameter` namespace.
"""

import pytest

from eprempy.parameter import default


@pytest.fixture
def srcdir():
    """Paths to a reference EPREM distribution."""
    return '~/emmrem/eprem/simulation/src'


@pytest.fixture
def reference():
    """All default parameter values, converted to underlying type."""
    defined = {
        'numNodesPerStream': {
            'type': int,
            'defaultVal': None,
            'minVal': None,
            'maxVal': default.BASETYPES_H['LARGEINT']['value'],
        },
        'numRowsPerFace': {
            'type': int,
            'defaultVal': 2,
            'minVal': 1,
            'maxVal': default.BASETYPES_H['LARGEINT']['value'],
        },
        'numColumnsPerFace': {
            'type': int,
            'defaultVal': 2,
            'minVal': 1,
            'maxVal': default.BASETYPES_H['LARGEINT']['value'],
        },
        'numEnergySteps': {
            'type': int,
            'defaultVal': 20,
            'minVal': 2,
            'maxVal': default.BASETYPES_H['LARGEINT']['value'],
        },
        'numMuSteps': {
            'type': int,
            'defaultVal': 20,
            'minVal': 2,
            'maxVal': default.BASETYPES_H['LARGEINT']['value'],
        },
        'rScale': {
            'type': float,
            'defaultVal': default.BASETYPES_H['RSAU']['value'],
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'flowMag': {
            'type': float,
            'defaultVal': 400.0e5,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'mhdDensityAu': {
            'type': float,
            'defaultVal': 8.30,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'mhdBAu': {
            'type': float,
            'defaultVal': 1.60e-5,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'simStartTime': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'tDel': {
            'type': float,
            'defaultVal': 0.01041666666667,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'simStopTime': {
            'type': float,
            'defaultVal': 0.01041666666667,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'numEpSteps': {
            'type': int,
            'defaultVal': 30,
            'minVal': 1,
            'maxVal': default.BASETYPES_H['LARGEINT']['value'],
        },
        'aziSunStart': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'omegaSun': {
            'type': float,
            'defaultVal': 0.001429813,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'lamo': {
            'type': float,
            'defaultVal': 1.0,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'dsh_min': {
            'type': float,
            'defaultVal': 5.0e-5,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'dsh_hel_min': {
            'type': float,
            'defaultVal': 2.5e-4,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'kperxkpar': {
            'type': float,
            'defaultVal': 0.01,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'mfpRadialPower': {
            'type': float,
            'defaultVal': 2.0,
            'minVal': -1.0 * default.BASETYPES_H['LARGEFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'rigidityPower': {
            'type': float,
            'defaultVal': 1 / 3,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'focusingLimit': {
            'type': float,
            'defaultVal': 1.0,
            'minVal': 0.0,
            'maxVal': 1.0,
        },
        'eMin': {
            'type': float,
            'defaultVal': 1.0,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'eMax': {
            'type': float,
            'defaultVal': 1000.0,
            'minVal': 1.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'useStochastic': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'useEPBoundary': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1,
        },
        'checkSeedPopulation': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1,
        },
        'seedFunctionTest': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'fluxLimiter': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1,
        },
        'gammaEhigh': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': -1.0 * default.BASETYPES_H['LARGEFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'gammaElow': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': -1.0 * default.BASETYPES_H['LARGEFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'FailModeDump': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1,
        },
        'outputFloat': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'unifiedOutput': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1,
        },
        'unifiedOutputTime': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'pointObserverOutput': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'pointObserverOutputTime': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'streamFluxOutput': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'streamFluxOutputTime': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'subTimeCouple': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'epremDomain': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'epremDomainOutputTime': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'unstructuredDomain': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'unstructuredDomainOutputTime': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'useAdiabaticChange': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1,
        },
        'useAdiabaticFocus': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1,
        },
        'useShellDiffusion': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'useParallelDiffusion': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1,
        },
        'useDrift': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'numSpecies': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 100,
        },
        'mass': {
            'type': list,
            'defaultVal': [1.0],
        },
        'charge': {
            'type': list,
            'defaultVal': [1.0],
        },
        'numObservers': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1000,
        },
        'obsTheta': {
            'type': list,
            'defaultVal': [0],
        },
        'obsPhi': {
            'type': list,
            'defaultVal': [0],
        },
        'idw_p': {
            'type': float,
            'defaultVal': 3.0,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'epEquilibriumCalcDuration': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'preEruptionDuration': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'parallelFlow': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'fieldAligned': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'epCalcStartTime': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'useBoundaryFunction': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1,
        },
        'boundaryFunctionInitDomain': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1,
        },
        'boundaryFunctAmplitude': {
            'type': float,
            'defaultVal': 1.0,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'boundaryFunctXi': {
            'type': float,
            'defaultVal': 1.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'boundaryFunctGamma': {
            'type': float,
            'defaultVal': 2.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'boundaryFunctBeta': {
            'type': float,
            'defaultVal': 2.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'boundaryFunctEcutoff': {
            'type': float,
            'defaultVal': 1.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'shockSolver': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'shockDetectPercent': {
            'type': float,
            'defaultVal': 1.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'minInjectionEnergy': {
            'type': float,
            'defaultVal': 0.01,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'shockInjectionFactor': {
            'type': float,
            'defaultVal': 1.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'idealShock': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'idealShockSharpness': {
            'type': float,
            'defaultVal': 1.0,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'idealShockScaleLength': {
            'type': float,
            'defaultVal': 0.0046491,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'idealShockJump': {
            'type': float,
            'defaultVal': 4.0,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'idealShockSpeed': {
            'type': float,
            'defaultVal': 1500e5,
            'minVal': default.BASETYPES_H['SMALLFLOAT']['value'],
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'idealShockInitTime': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['LARGEFLOAT']['value'],
        },
        'idealShockTheta': {
            'type': float,
            'defaultVal': default.BASETYPES_H['HALF_PI']['value'],
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['PI']['value'],
        },
        'idealShockPhi': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': 2.0 * default.BASETYPES_H['PI']['value'],
        },
        'idealShockWidth': {
            'type': float,
            'defaultVal': 0.0,
            'minVal': 0.0,
            'maxVal': default.BASETYPES_H['PI']['value'],
        },
        'dumpFreq': {
            'type': int,
            'defaultVal': 1,
            'minVal': 0,
            'maxVal': 1000000,
        },
        'outputRestart': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1000000,
        },
        'dumpOnAbort': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'saveRestartFile': {
            'type': int,
            'defaultVal': 0,
            'minVal': 0,
            'maxVal': 1,
        },
        'warningsFile': {
            'type': str,
            'defaultVal': 'warningsXXX.txt',
        },
    }
    defined['obsR'] = {
        'type': list,
        'defaultVal': [defined['rScale']['defaultVal']],
    }
    return defined


