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
    'reference energy': {
        'aliases': ['energy0'],
        'unit': 'MeV',
        'default': 1.0,
    },
    'reference radius': {
        'aliases': ['r0'],
        'unit': 'au',
        'default': 1.0,
    },
}
"""Metadata for post-processing parameters."""


# TODO: Add ENLIL-related parameters to _CONFIGURATION_C and _BASETYPES_H


_CONFIGURATION_C = {
    'adiabaticChangeAlg': {
        'aliases': [],
        'unit': None,
    },
    'adiabaticFocusAlg': {
        'aliases': [],
        'unit': None,
    },
    'boundaryFunctAmplitude': {
        'aliases': ['J0'],
        'unit': '1 / (cm^2 * s * sr * (MeV/nuc))',
    },
    'boundaryFunctXi': {
        'aliases': ['xi'],
        'unit': '1',
    },
    'boundaryFunctBeta': {
        'aliases': ['beta'],
        'unit': '1',
    },
    'boundaryFunctGamma': {
        'aliases': ['gamma'],
        'unit': '1',
    },
    'boundaryFunctEcutoff': {
        'aliases': ['E0'],
        'unit': 'MeV',
    },
    'kperxkpar': {
        'aliases': ['kper_kpar', 'kper/kpar', 'kper / kpar'],
        'unit': '1',
    },
    'lamo': {
        'aliases': ['lam0', 'lambda0'],
        'unit': 'au',
    },
    'mfpRadialPower': {
        'aliases': ['mfp_radial_power'],
        'unit': '1',
    },
    'nodeAdvance': {
        'aliases': [],
        'unit': None,
    },
    'nodeInit': {
        'aliases': [],
        'unit': None,
    },
    'nodeInitSuccess': {
        'aliases': [],
        'unit': None,
    },
    'nodeInitTimeStep': {
        'aliases': [],
        'unit': 'day',
    },
    'nodeRadialMax': {
        'aliases': [],
        'unit': 'au',
    },
    'nodeRadialMin': {
        'aliases': [],
        'unit': 'au',
    },
    'rigidityPower': {
        'aliases': ['rigidity_power'],
        'unit': '1',
    },
    'flowMag': {
        'aliases': [],
        'unit': 'km/s',
    },
    'mhdDensityAu': {
        'aliases': [],
        'unit': 'cm^-3',
    },
    'mhdBAu': {
        'aliases': [],
        'unit': 'G',
    },
    'omegaSun': {
        'aliases': [],
        'unit': 'rad * cm / (au * s)',
    },
    'mass': {
        'aliases': [],
        'unit': 'nucleon',
    },
    'charge': {
        'aliases': [],
        'unit': 'e',
    },
    'minInjectionEnergy': {
        'aliases': [],
        'unit': 'MeV',
    },
    'maxInjectionEnergy': {
        'aliases': [],
        'unit': 'MeV',
    },
    'shockInjectionFactor': {
        'aliases': [],
        'unit': '1',
    },
    'shockDetectPercent': {
        'aliases': [],
        'unit': '1',
    },
    'rScale': {
        'aliases': [],
        'unit': 'au',
    },
    'simStartTime': {
        'aliases': [],
        'unit': 'day',
    },
    'simStopTime': {
        'aliases': [],
        'unit': 'day',
    },
    'eMin': {
        'aliases': [],
        'unit': 'MeV/nuc',
    },
    'eMax': {
        'aliases': [],
        'unit': 'MeV/nuc',
    },
    'numObservers': {
        'aliases': [],
        'unit': '1',
    },
    'obsR': {
        'aliases': [],
        'unit': 'au',
    },
    'obsTheta': {
        'aliases': [],
        'unit': 'rad',
    },
    'obsPhi': {
        'aliases': [],
        'unit': 'rad',
    },
    'idw_p': {
        'aliases': [],
        'unit': '1',
    },
    'idealShockSharpness': {
        'aliases': [],
        'unit': '1',
    },
    'idealShockScaleLength': {
        'aliases': [],
        'unit': 'au',
    },
    'idealShockJump': {
        'aliases': [],
        'unit': '1',
    },
    'idealShockSpeed': {
        'aliases': [],
        'unit': 'km/s',
    },
    'idealShockInitTime': {
        'aliases': [],
        'unit': 'day',
    },
    'idealShockTheta': {
        'aliases': [],
        'unit': 'rad',
    },
    'idealShockPhi': {
        'aliases': [],
        'unit': 'rad',
    },
    'idealShockWidth': {
        'aliases': [],
        'unit': 'rad',
    },
    'tDel': {
        'aliases': [],
        'unit': 'day',
    },
    'gammaElow': {
        'aliases': [],
        'unit': '1',
    },
    'gammaEhigh': {
        'aliases': [],
        'unit': '1',
    },
    'masInitTimeStep': {
        'aliases': [],
        'unit': 'day',
    },
    'masStartTime': {
        'aliases': [],
        'unit': 'day',
    },
    'epEquilibriumCalcDuration': {
        'aliases': [],
        'unit': 'day',
    },
    'preEruptionDuration': {
        'aliases': [],
        'unit': 'day',
    },
    'pointObserverOutput': {
        'aliases': [],
        'unit': None,
    },
    'enlilCouple': {
        'aliases': [],
        'unit': None,
    },
    'outputFloat': {
        'aliases': [],
        'unit': None,
    },
    'numRowsPerFace': {
        'aliases': [],
        'unit': None,
    },
    'numColumnsPerFace': {
        'aliases': [],
        'unit': None,
    },
    'numNodesPerStream': {
        'aliases': [],
        'unit': None,
    },
    'numEnergySteps': {
        'aliases': [],
        'unit': None,
    },
    'numMuSteps': {
        'aliases': [],
        'unit': None,
    },
    'useDrift': {
        'aliases': [],
        'unit': None,
    },
    'useShellDiffusion': {
        'aliases': [],
        'unit': None,
    },
    'unifiedOutput': {
        'aliases': [],
        'unit': None,
    },
    'unifiedOutputTime': {
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
    'unstructuredDomainOutputTime': {
        'aliases': [],
        'unit': 'day',
    },
    'pointObserverOutputTime': {
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
    'epCalcStartTime': {
        'aliases': [],
        'unit': 'day',
    },
    'dumpFreq': {
        'aliases': [],
        'unit': None,
    },
    'aziSunStart': {
        'aliases': [],
        'unit': 'rad',
    },
    'idealShock': {
        'aliases': [],
        'unit': None,
    },
    'shockSolver': {
        'aliases': [],
        'unit': None,
    },
    'fluxLimiter': {
        'aliases': [],
        'unit': None,
    },
    'numEpSteps': {
        'aliases': [],
        'unit': None,
    },
    'useParallelDiffusion': {
        'aliases': [],
        'unit': None,
    },
    'useAdiabaticChange': {
        'aliases': [],
        'unit': None,
    },
    'useAdiabaticFocus': {
        'aliases': [],
        'unit': None,
    },
    'numSpecies': {
        'aliases': [],
        'unit': None,
    },
    'boundaryFunctionInitDomain': {
        'aliases': [],
        'unit': None,
    },
    'checkSeedPopulation': {
        'aliases': [],
        'unit': None,
    },
    'subTimeCouple': {
        'aliases': [],
        'unit': None,
    },
    'FailModeDump': {
        'aliases': [],
        'unit': None,
    },
    'masCouple': {
        'aliases': [],
        'unit': None,
    },
    'masDirectory': {
        'aliases': [],
        'unit': None,
    },
    'masInitFromOuterBoundary': {
        'aliases': [],
        'unit': None,
    },
    'masRotateSolution': {
        'aliases': [],
        'unit': None,
    },
    'useMasSteadyStateDt': {
        'aliases': [],
        'unit': None,
    },
    'masDigits': {
        'aliases': [],
        'unit': None,
    },
}
"""Metadata for parameters defined in `configuration.c`."""


_BASETYPES_H = {
    'T': {
        'info': 'True',
        'unit': None,
        'type': int,
    },
    'F': {
        'info': 'False',
        'unit': None,
        'type': int,
    },
    'PI': {
        'info': 'The value of π.',
        'unit': None,
        'type': float,
    },
    'TWO_PI': {
        'info': 'The value of 2π.',
        'unit': None,
        'type': float,
    },
    'VERYSMALL': {
        'info': 'A very small value.',
        'unit': None,
        'type': float,
    },
    'BADVALUE': {
        'info': 'A bad (invalid) float value.',
        'unit': None,
        'type': float,
    },
    'BADINT': {
        'info': 'A bad (invalid) integer value.',
        'unit': None,
        'type': int,
    },
    'MP': {
        'info': 'The proton mass.',
        'unit': 'g',
        'type': float,
    },
    'EV': {
        'info': 'The conversion from eVs to ergs.',
        'unit': 'erg/eV',
        'type': float,
    },
    'MEV': {
        'info': 'The conversion from MeVs to ergs.',
        'unit': 'erg/MeV',
        'type': float,
    },
    'GEV': {
        'info': 'The conversion from GeVs to ergs.',
        'unit': 'erg/GeV',
        'type': float,
    },
    'Q': {
        'info': 'The proton charge.',
        'unit': 'statC',
        'type': float,
    },
    'C': {
        'info': 'The speed of light.',
        'unit': 'cm/s',
        'type': float,
    },
    'MZERO': {
        'info': 'The proton rest-mass energy in GeV.',
        'unit': 'GeV',
        'type': float,
    },
    'AU': {
        'info': 'One astronomical unit.',
        'unit': 'cm',
        'type': float,
    },
    'RSUN': {
        'info': 'The value of the solar radius.',
        'unit': 'cm',
        'type': float,
    },
    'RSAU': {
        'info': 'The number of solar radii per au.',
        'unit': '1',
        'type': float,
    },
    'TAU': {
        'info': 'The canonical EPREM time scale.',
        'unit': 's',
        'type': float,
    },
    'DAY': {
        'info': 'The conversion from EPREM time steps to Julian days.',
        'unit': 'day',
        'type': float,
    },
    'MHD_DENSITY_NORM': {
        'info': 'The normalization factor for density.',
        'unit': '1',
        'type': float,
    },
    'MHD_B_NORM': {
        'info': 'The normalization for magnetic fields.',
        'unit': '1',
        'type': float,
    },
    'OM': {
        'info': 'The normalization for ion gyrofrequency.',
        'unit': '1',
        'type': float,
    },
    'FCONVERT': {
        'info': 'The conversion from distribution to flux.',
        'unit': '1',
        'type': float,
    },
    'VOLT': {
        'info': 'The conversion from volts to statvolts.',
        'unit': '1',
        'type': float,
    },
    'THRESH': {
        'info': 'The threshold for perpendicular diffusion.',
        'unit': '1',
        'type': float,
    },
    'MAS_TIME_NORM': {
        'info': 'The MAS time normalization factor.',
        'unit': '1',
        'type': float,
    },
    'MAS_LENGTH_NORM': {
        'info': 'The MAS length normalization factor.',
        'unit': '1',
        'type': float,
    },
    'MAS_RHO_NORM': {
        'info': 'The MAS plasma-density normalization.',
        'unit': '1',
        'type': float,
    },
    'MAS_TIME_CONVERT': {
        'info': 'The time conversion from MAS units.',
        'unit': '1',
        'type': float,
    },
    'MAS_V_CONVERT': {
        'info': 'The velocity conversion from MAS units.',
        'unit': '1',
        'type': float,
    },
    'MAS_RHO_CONVERT': {
        'info': 'The density conversion from MAS units.',
        'unit': '1',
        'type': float,
    },
    'MAS_B_CONVERT': {
        'info': 'The magnetic field conversion from MAS units.',
        'unit': '1',
        'type': float,
    },
    'MAX_STRING_SIZE': {
        'info': '',
        'unit': None,
        'type': int,
    },
    'MHD_DEFAULT': {
        'info': 'Use the default MHD solver.',
        'unit': None,
        'type': int,
    },
    'MHD_ENLIL': {
        'info': 'Use ENLIL for MHD values.',
        'unit': None,
        'type': int,
    },
    'MHD_LFMH': {
        'info': 'Use LFM for MHD values.',
        'unit': None,
        'type': int,
    },
    'MHD_BATSRUS': {
        'info': 'Use BATS-R-US for MHD values.',
        'unit': None,
        'type': int,
    },
    'MHD_MAS': {
        'info': 'Use MAS for MHD values.',
        'unit': None,
        'type': int,
    },
    'NUM_MPI_BOUNDARY_FLDS': {
        'info': 'Number of MPI psuedo-fields for use in creating MPI typedefs.',
        'unit': None,
        'type': int,
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


