"""
Configuration file for the `test_parameter` namespace.
"""

import pytest

from eprempy.parameter import default


@pytest.fixture
def srcdir():
    """Paths to a reference EPREM distribution."""
    return '~/emmrem/open/source/eprem/src'


@pytest.fixture
def reference():
    """All default parameter values, converted to underlying type."""
    return {
        'numNodesPerStream': {
            'type': int,
            'default': None,
            'minimum': None,
            'maximum': default.BASETYPES_H['BADINT']['value'],
        },
        'numRowsPerFace': {
            'type': int,
            'default': 2,
            'minimum': 1,
            'maximum': default.BASETYPES_H['BADINT']['value'],
        },
        'numColumnsPerFace': {
            'type': int,
            'default': 2,
            'minimum': 1,
            'maximum': default.BASETYPES_H['BADINT']['value'],
        },
        'numEnergySteps': {
            'type': int,
            'default': 20,
            'minimum': 2,
            'maximum': default.BASETYPES_H['BADINT']['value'],
        },
        'numMuSteps': {
            'type': int,
            'default': 20,
            'minimum': 2,
            'maximum': default.BASETYPES_H['BADINT']['value'],
        },
        'rScale': {
            'type': float,
            'default': default.BASETYPES_H['RSAU']['value'],
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'flowMag': {
            'type': float,
            'default': 400.0e5,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'mhdDensityAu': {
            'type': float,
            'default': 8.30,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'mhdBAu': {
            'type': float,
            'default': 1.60e-5,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'simStartTime': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'tDel': {
            'type': float,
            'default': 0.01041666666667,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'simStopTime': {
            'type': float,
            'default': 0.01041666666667,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'numEpSteps': {
            'type': int,
            'default': 30,
            'minimum': 1,
            'maximum': default.BASETYPES_H['BADINT']['value'],
        },
        'aziSunStart': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'omegaSun': {
            'type': float,
            'default': 0.001429813,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'lamo': {
            'type': float,
            'default': 1.0,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'dsh_min': {
            'type': float,
            'default': 5.0e-5,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'dsh_hel_min': {
            'type': float,
            'default': 2.5e-4,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'kperxkpar': {
            'type': float,
            'default': 0.01,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'mfpRadialPower': {
            'type': float,
            'default': 2.0,
            'minimum': -1.0 * default.BASETYPES_H['BADVALUE']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'rigidityPower': {
            'type': float,
            'default': 1 / 3,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'focusingLimit': {
            'type': float,
            'default': 1.0,
            'minimum': 0.0,
            'maximum': 1.0,
        },
        'eMin': {
            'type': float,
            'default': 1.0,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'eMax': {
            'type': float,
            'default': 1000.0,
            'minimum': 1.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'useStochastic': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'useEPBoundary': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1,
        },
        'checkSeedPopulation': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1,
        },
        'seedFunctionTest': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'fluxLimiter': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1,
        },
        'gammaEhigh': {
            'type': float,
            'default': 0.0,
            'minimum': -1.0 * default.BASETYPES_H['BADVALUE']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'gammaElow': {
            'type': float,
            'default': 0.0,
            'minimum': -1.0 * default.BASETYPES_H['BADVALUE']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'FailModeDump': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1,
        },
        'outputFloat': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'unifiedOutput': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1,
        },
        'unifiedOutputTime': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'pointObserverOutput': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'pointObserverOutputTime': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'streamFluxOutput': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'streamFluxOutputTime': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'subTimeCouple': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'epremDomain': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'epremDomainOutputTime': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'unstructuredDomain': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'unstructuredDomainOutputTime': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'useAdiabaticChange': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1,
        },
        'useAdiabaticFocus': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1,
        },
        'useShellDiffusion': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'useParallelDiffusion': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1,
        },
        'useDrift': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'numSpecies': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 100,
        },
        'mass': {
            'type': list,
            'default': [1.0],
        },
        'charge': {
            'type': list,
            'default': [1.0],
        },
        'numObservers': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1000,
        },
        'obsR': {
            'type': list,
            'default': [0],
        },
        'obsTheta': {
            'type': list,
            'default': [0],
        },
        'obsPhi': {
            'type': list,
            'default': [0],
        },
        'idw_p': {
            'type': float,
            'default': 3.0,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'epEquilibriumCalcDuration': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'preEruptionDuration': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'parallelFlow': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'fieldAligned': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'epCalcStartTime': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'useBoundaryFunction': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1,
        },
        'boundaryFunctionInitDomain': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1,
        },
        'boundaryFunctAmplitude': {
            'type': float,
            'default': 1.0,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'boundaryFunctXi': {
            'type': float,
            'default': 1.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'boundaryFunctGamma': {
            'type': float,
            'default': 2.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'boundaryFunctBeta': {
            'type': float,
            'default': 1.7,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'boundaryFunctEcutoff': {
            'type': float,
            'default': 1.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'shockSolver': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'shockDetectPercent': {
            'type': float,
            'default': 1.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'minInjectionEnergy': {
            'type': float,
            'default': 0.01,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'shockInjectionFactor': {
            'type': float,
            'default': 1.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'idealShock': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'idealShockSharpness': {
            'type': float,
            'default': 1.0,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'idealShockScaleLength': {
            'type': float,
            'default': 0.0046491,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'idealShockJump': {
            'type': float,
            'default': 4.0,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'idealShockSpeed': {
            'type': float,
            'default': 1500e5,
            'minimum': default.BASETYPES_H['VERYSMALL']['value'],
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'idealShockInitTime': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['BADVALUE']['value'],
        },
        'idealShockTheta': {
            'type': float,
            'default': 1.570796,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['PI']['value'],
        },
        'idealShockPhi': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': 2.0 * default.BASETYPES_H['PI']['value'],
        },
        'idealShockWidth': {
            'type': float,
            'default': 0.0,
            'minimum': 0.0,
            'maximum': default.BASETYPES_H['PI']['value'],
        },
        'dumpFreq': {
            'type': int,
            'default': 1,
            'minimum': 0,
            'maximum': 1000000,
        },
        'outputRestart': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1000000,
        },
        'dumpOnAbort': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'saveRestartFile': {
            'type': int,
            'default': 0,
            'minimum': 0,
            'maximum': 1,
        },
        'warningsFile': {
            'type': str,
            'default': 'warningsXXX.txt',
        },
    }

