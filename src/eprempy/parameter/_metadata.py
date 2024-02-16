"""
Metadata for EPREM simulation parameters.
"""

from .. import aliased


_LOCAL = {
    'minimum_energy': {
        'aliases': ['Emin', 'minimum energy'],
        'unit': 'MeV',
        'default': 0.0,
    },
}
"""Metadata for post-processing parameters."""


# TODO: Add ENLIL-related parameters to _CONFIGURATION_C and _BASETYPES_H


_CONFIGURATION_C = {
    'FailModeDump': {
        'aliases': [],
        'unit': None,
    },
    'adiabaticChangeAlg': {
        'aliases': [],
        'unit': None,
    },
    'adiabaticFocusAlg': {
        'aliases': [],
        'unit': None,
    },
    'aziSunStart': {
        'aliases': [],
        'unit': 'rad',
    },
    'boundaryFunctAmplitude': {
        'aliases': ['J0'],
        'unit': '1 / (cm^2 * s * sr * (MeV/nuc))',
    },
    'boundaryFunctBeta': {
        'aliases': ['beta'],
        'unit': '1',
    },
    'boundaryFunctEcutoff': {
        'aliases': ['E0'],
        'unit': 'MeV',
    },
    'boundaryFunctEr': {
        'aliases': ['Er', 'reference energy'],
        'unit': 'MeV',
    },
    'boundaryFunctGamma': {
        'aliases': ['gamma'],
        'unit': '1',
    },
    'boundaryFunctR0': {
        'aliases': ['R0', 'r0', 'reference radius'],
        'unit': 'au',
    },
    'boundaryFunctXi': {
        'aliases': ['xi'],
        'unit': '1',
    },
    'boundaryFunctionInitDomain': {
        'aliases': [],
        'unit': None,
    },
    'charge': {
        'aliases': [],
        'unit': 'e',
    },
    'checkSeedPopulation': {
        'aliases': [],
        'unit': None,
    },
    'dumpFreq': {
        'aliases': [],
        'unit': None,
    },
    'eMax': {
        'aliases': [],
        'unit': 'MeV/nuc',
    },
    'eMin': {
        'aliases': [],
        'unit': 'MeV/nuc',
    },
    'epCalcStartTime': {
        'aliases': [],
        'unit': 'day',
    },
    'epEquilibriumCalcDuration': {
        'aliases': [],
        'unit': 'day',
    },
    'epremDomain': {
        'aliases': [],
        'unit': None,
    },
    'epremDomainOutputTime': {
        'aliases': [],
        'unit': 'day',
    },
    'flowMag': {
        'aliases': [],
        'unit': 'cm/s',
    },
    'fluxLimiter': {
        'aliases': [],
        'unit': None,
    },
    'gammaEhigh': {
        'aliases': [],
        'unit': '1',
    },
    'gammaElow': {
        'aliases': [],
        'unit': '1',
    },
    'idealShock': {
        'aliases': [],
        'unit': None,
    },
    'idealShockFalloff': {
        'aliases': [],
        'unit': None,
    },
    'idealShockInitTime': {
        'aliases': [],
        'unit': 'day',
    },
    'idealShockJump': {
        'aliases': [],
        'unit': '1',
    },
    'idealShockPhi': {
        'aliases': [],
        'unit': 'rad',
    },
    'idealShockPhiWidth': {
        'aliases': [],
        'unit': 'rad',
    },
    'idealShockScale': {
        'aliases': [],
        'unit': 'au',
    },
    'idealShockScaleLength': {
        'aliases': [],
        'unit': 'au',
    },
    'idealShockSharpness': {
        'aliases': [],
        'unit': '1',
    },
    'idealShockSpeed': {
        'aliases': [],
        'unit': 'cm/s',
    },
    'idealShockTheta': {
        'aliases': [],
        'unit': 'rad',
    },
    'idealShockThetaWidth': {
        'aliases': [],
        'unit': 'rad',
    },
    'idealShockUseDegrees': {
        'aliases': [],
        'unit': None,
    },
    'idealShockWidth': {
        'aliases': [],
        'unit': 'rad',
    },
    'idw_p': {
        'aliases': [],
        'unit': '1',
    },
    'kperxkpar': {
        'aliases': ['kper_kpar', 'kper/kpar', 'kper / kpar'],
        'unit': '1',
    },
    'lamo': {
        'aliases': ['lam0', 'lambda0'],
        'unit': 'au',
    },
    'mass': {
        'aliases': [],
        'unit': 'nucleon',
    },
    'mfpRadialPower': {
        'aliases': ['mfp_radial_power'],
        'unit': '1',
    },
    'mhdBAu': {
        'aliases': [],
        'unit': 'G',
    },
    'mhdBConvert': {
        'aliases': [],
        'unit': '1',
    },
    'mhdCouple': {
        'aliases': [],
        'unit': None,
    },
    'mhdCoupledTime': {
        'aliases': [],
        'unit': None,
    },
    'mhdDigits': {
        'aliases': [],
        'unit': None,
    },
    'mhdDirectory': {
        'aliases': [],
        'unit': None,
    },
    'mhdInitFromOuterBoundary': {
        'aliases': [],
        'unit': None,
    },
    'mhdDensityAu': {
        'aliases': [],
        'unit': 'cm^-3',
    },
    'mhdInitRadius': {
        'aliases': [],
        'unit': 'au',
    },
    'mhdInitTimeStep': {
        'aliases': [],
        'unit': 'day',
    },
    'mhdNumFiles': {
        'aliases': [],
        'unit': None,
    },
    'mhdRadialMax': {
        'aliases': [],
        'unit': 'au',
    },
    'mhdRadialMin': {
        'aliases': [],
        'unit': 'au',
    },
    'mhdRhoConvert': {
        'aliases': [],
        'unit': '1',
    },
    'mhdRotateSolution': {
        'aliases': [],
        'unit': None,
    },
    'mhdStartTime': {
        'aliases': [],
        'unit': 'day',
    },
    'mhdSteadyState': {
        'aliases': [],
        'unit': None,
    },
    'mhdTimeConvert': {
        'aliases': [],
        'unit': '1',
    },
    'mhdVConvert': {
        'aliases': [],
        'unit': '1',
    },
    'mhdVmin': {
        'aliases': [],
        'unit': 'cm/s',
    },
    'mhdVmax': {
        'aliases': [],
        'unit': 'cm/s',
    },
    'minInjectionEnergy': {
        'aliases': [],
        'unit': 'MeV',
    },
    'numColumnsPerFace': {
        'aliases': [],
        'unit': None,
    },
    'numEnergySteps': {
        'aliases': [],
        'unit': None,
    },
    'numEpSteps': {
        'aliases': [],
        'unit': None,
    },
    'numMuSteps': {
        'aliases': [],
        'unit': None,
    },
    'numNodesPerStream': {
        'aliases': [],
        'unit': None,
    },
    'numObservers': {
        'aliases': [],
        'unit': '1',
    },
    'numRowsPerFace': {
        'aliases': [],
        'unit': None,
    },
    'numSpecies': {
        'aliases': [],
        'unit': None,
    },
    'obsPhi': {
        'aliases': [],
        'unit': 'rad',
    },
    'obsR': {
        'aliases': [],
        'unit': 'au',
    },
    'obsTheta': {
        'aliases': [],
        'unit': 'rad',
    },
    'obsUseDegrees': {
        'aliases': [],
        'unit': None,
    },
    'omegaSun': {
        'aliases': [],
        'unit': 'rad * cm / (au * s)',
    },
    'outputFloat': {
        'aliases': [],
        'unit': None,
    },
    'pointObserverOutput': {
        'aliases': [],
        'unit': None,
    },
    'pointObserverOutputTime': {
        'aliases': [],
        'unit': 'day',
    },
    'preEruptionDuration': {
        'aliases': [],
        'unit': 'day',
    },
    'rScale': {
        'aliases': [],
        'unit': 'au',
    },
    'rigidityPower': {
        'aliases': ['rigidity_power'],
        'unit': '1',
    },
    'shockDetectPercent': {
        'aliases': [],
        'unit': '1',
    },
    'shockInjectionFactor': {
        'aliases': [],
        'unit': '1',
    },
    'shockSolver': {
        'aliases': [],
        'unit': None,
    },
    'simStartTime': {
        'aliases': [],
        'unit': 'day',
    },
    'simStopTime': {
        'aliases': [],
        'unit': 'day',
    },
    'streamFluxOutput': {
        'aliases': [],
        'unit': None,
    },
    'streamFluxOutputTime': {
        'aliases': [],
        'unit': 'day',
    },
    'streamSpawnLocAzi': {
        'aliases': [],
        'unit': 'rad',
    },
    'streamSpawnLocZen': {
        'aliases': [],
        'unit': 'rad',
    },
    'subTimeCouple': {
        'aliases': [],
        'unit': None,
    },
    'tDel': {
        'aliases': [],
        'unit': 'day',
    },
    'unifiedOutput': {
        'aliases': [],
        'unit': None,
    },
    'unifiedOutputTime': {
        'aliases': [],
        'unit': 'day',
    },
    'unstructuredDomain': {
        'aliases': [],
        'unit': None,
    },
    'unstructuredDomainOutputTime': {
        'aliases': [],
        'unit': 'day',
    },
    'useAdiabaticChange': {
        'aliases': [],
        'unit': None,
    },
    'useAdiabaticFocus': {
        'aliases': [],
        'unit': None,
    },
    'useDrift': {
        'aliases': [],
        'unit': None,
    },
    'useManualStreamSpawnLoc': {
        'aliases': [],
        'unit': None,
    },
    'useMhdSteadyStateDt': {
        'aliases': [],
        'unit': None,
    },
    'useParallelDiffusion': {
        'aliases': [],
        'unit': None,
    },
    'useShellDiffusion': {
        'aliases': [],
        'unit': None,
    },
    'warningsFile': {
        'aliases': [],
        'unit': None,
    },
}
"""Metadata for parameters defined in `configuration.c`."""


_BASETYPES_H = {
    'AU': {
        'info': 'One astronomical unit.',
        'unit': 'cm',
        'type': float,
    },
    'C': {
        'info': 'The speed of light.',
        'unit': 'cm/s',
        'type': float,
    },
    'DAY': {
        'info': 'The conversion from EPREM time steps to Julian days.',
        'unit': 'day',
        'type': float,
    },
    'DEG2RAD': {
        'info': 'The conversion from degrees to radians.',
        'unit': '1',
        'type': float,
    },
    'EV': {
        'info': 'The conversion from eVs to ergs.',
        'unit': 'erg/eV',
        'type': float,
    },
    'F': {
        'info': 'False',
        'unit': None,
        'type': int,
    },
    'FCONVERT': {
        'info': 'The conversion from distribution to flux.',
        'unit': '1',
        'type': float,
    },
    'GEV': {
        'info': 'The conversion from GeVs to ergs.',
        'unit': 'erg/GeV',
        'type': float,
    },
    'HALF_PI': {
        'info': 'The value of π/2.',
        'unit': None,
        'type': float,
    },
    'LARGEFLOAT': {
        'info': 'A very large float value.',
        'unit': None,
        'type': float,
    },
    'LARGEINT': {
        'info': 'A very large integer value.',
        'unit': None,
        'type': int,
    },
    'MAX_STRING_SIZE': {
        'info': '',
        'unit': None,
        'type': int,
    },
    'MEV': {
        'info': 'The conversion from MeVs to ergs.',
        'unit': 'erg/MeV',
        'type': float,
    },
    'MHD_B_NORM': {
        'info': 'The normalization for magnetic fields.',
        'unit': '1',
        'type': float,
    },
    'MHD_COUPLED': {
        'info': 'Couple to external MHD',
        'unit': None,
        'type': int,
    },
    'MHD_DEFAULT': {
        'info': 'Use the default MHD solver.',
        'unit': None,
        'type': int,
    },
    'MHD_DENSITY_NORM': {
        'info': 'The normalization factor for density.',
        'unit': '1',
        'type': float,
    },
    'MP': {
        'info': 'The proton mass.',
        'unit': 'g',
        'type': float,
    },
    'MZERO': {
        'info': 'The proton rest-mass energy in GeV.',
        'unit': 'GeV',
        'type': float,
    },
    'OM': {
        'info': 'The normalization for ion gyrofrequency.',
        'unit': '1',
        'type': float,
    },
    'PI': {
        'info': 'The value of π.',
        'unit': None,
        'type': float,
    },
    'Q': {
        'info': 'The proton charge.',
        'unit': 'statC',
        'type': float,
    },
    'RAD2DEG': {
        'info': 'The conversion from radians to degrees.',
        'unit': '1',
        'type': float,
    },
    'RSAU': {
        'info': 'The number of solar radii per au.',
        'unit': '1',
        'type': float,
    },
    'RSUN': {
        'info': 'The value of the solar radius.',
        'unit': 'cm',
        'type': float,
    },
    'SMALLFLOAT': {
        'info': 'A very small float value.',
        'unit': None,
        'type': float,
    },
    'T': {
        'info': 'True',
        'unit': None,
        'type': int,
    },
    'TAU': {
        'info': 'The canonical EPREM time scale.',
        'unit': 's',
        'type': float,
    },
    'THRESH': {
        'info': 'The threshold for perpendicular diffusion.',
        'unit': '1',
        'type': float,
    },
    'TWO_PI': {
        'info': 'The value of 2π.',
        'unit': None,
        'type': float,
    },
    'VOLT': {
        'info': 'The conversion from volts to statvolts.',
        'unit': '1',
        'type': float,
    },
}
"""Metadata for parameters defined in `baseTypes.h`."""

_metadata = {**_LOCAL, **_CONFIGURATION_C, **_BASETYPES_H}
"""Combined metadata dictionary for internal use."""

METADATA = aliased.Mapping(_metadata)
"""Metadata for EPREM parameters."""

NAMES = aliased.NameMap(_metadata)
"""A mapping from alias(es) to EPREM parameter."""

ALIASES = aliased.Groups(*METADATA.keys(aliased=True))
"""Groups of aliases for EPREM parameters."""

UNITS = {
    key: info.get('unit')
    for key, info in _metadata.items()
}
"""Collection of units from metadata."""


