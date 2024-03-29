"""
Default values and metadata for EPREM simulation parameters.

DO NOT EDIT THIS FILE. It was created via the default-parameters.py CLI.
Run `python /home/matthew/emmrem/eprem/py/scripts/default-parameters.py -h` for more information.
"""


BASETYPES_H = {
    'AU': {
        'value': 14959787070000.0,
        'info': 'One astronomical unit.',
        'unit': 'cm',
        'type': float,
    },
    'C': {
        'value': 29979245800.0,
        'info': 'The speed of light.',
        'unit': 'cm/s',
        'type': float,
    },
    'DAY': {
        'value': 0.0057755183314369945,
        'info': 'The conversion from EPREM time steps to Julian days.',
        'unit': 'day',
        'type': float,
    },
    'DEG2RAD': {
        'value': 0.017453292519943295,
        'info': 'The conversion from degrees to radians.',
        'unit': '1',
        'type': float,
    },
    'EV': {
        'value': 1.6022e-12,
        'info': 'The conversion from eVs to ergs.',
        'unit': 'erg/eV',
        'type': float,
    },
    'F': {
        'value': 0,
        'info': 'False',
        'unit': None,
        'type': int,
    },
    'FCONVERT': {
        'value': 1.2379901472361203e-12,
        'info': 'The conversion from distribution to flux.',
        'unit': '1',
        'type': float,
    },
    'GEV': {
        'value': 0.0016022,
        'info': 'The conversion from GeVs to ergs.',
        'unit': 'erg/GeV',
        'type': float,
    },
    'HALF_PI': {
        'value': 1.5707963267948966,
        'info': 'The value of π/2.',
        'unit': None,
        'type': float,
    },
    'LARGEFLOAT': {
        'value': 1e+33,
        'info': 'A very large float value.',
        'unit': None,
        'type': float,
    },
    'LARGEINT': {
        'value': 2147483647,
        'info': 'A very large integer value.',
        'unit': None,
        'type': int,
    },
    'MAX_STRING_SIZE': {
        'value': 240,
        'info': '',
        'unit': None,
        'type': int,
    },
    'MEV': {
        'value': 1.6022e-06,
        'info': 'The conversion from MeVs to ergs.',
        'unit': 'erg/MeV',
        'type': float,
    },
    'MHD_B_NORM': {
        'value': 0.038771870111656996,
        'info': 'The normalization for magnetic fields.',
        'unit': '1',
        'type': float,
    },
    'MHD_COUPLED': {
        'value': 1,
        'info': 'Couple to external MHD',
        'unit': None,
        'type': int,
    },
    'MHD_DEFAULT': {
        'value': 0,
        'info': 'Use the default MHD solver.',
        'unit': None,
        'type': int,
    },
    'MHD_DENSITY_NORM': {
        'value': 1.0,
        'info': 'The normalization factor for density.',
        'unit': '1',
        'type': float,
    },
    'MP': {
        'value': 1.6726e-24,
        'info': 'The proton mass.',
        'unit': 'g',
        'type': float,
    },
    'MZERO': {
        'value': 0.9382461065754594,
        'info': 'The proton rest-mass energy in GeV.',
        'unit': 'GeV',
        'type': float,
    },
    'OM': {
        'value': 185327.43617160583,
        'info': 'The normalization for ion gyrofrequency.',
        'unit': '1',
        'type': float,
    },
    'PI': {
        'value': 3.141592653589793,
        'info': 'The value of π.',
        'unit': None,
        'type': float,
    },
    'Q': {
        'value': 4.80320425e-10,
        'info': 'The proton charge.',
        'unit': 'statC',
        'type': float,
    },
    'RAD2DEG': {
        'value': 57.29577951308232,
        'info': 'The conversion from radians to degrees.',
        'unit': '1',
        'type': float,
    },
    'RSAU': {
        'value': 0.0046524726370988385,
        'info': 'The number of solar radii per au.',
        'unit': '1',
        'type': float,
    },
    'RSUN': {
        'value': 69600000000.0,
        'info': 'The value of the solar radius.',
        'unit': 'cm',
        'type': float,
    },
    'SMALLFLOAT': {
        'value': 1e-33,
        'info': 'A very small float value.',
        'unit': None,
        'type': float,
    },
    'T': {
        'value': 1,
        'info': 'True',
        'unit': None,
        'type': int,
    },
    'TAU': {
        'value': 499.0047838361564,
        'info': 'The canonical EPREM time scale.',
        'unit': 's',
        'type': float,
    },
    'THRESH': {
        'value': 0.025,
        'info': 'The threshold for perpendicular diffusion.',
        'unit': '1',
        'type': float,
    },
    'TWO_PI': {
        'value': 6.283185307179586,
        'info': 'The value of 2π.',
        'unit': None,
        'type': float,
    },
    'VOLT': {
        'value': 0.0033333,
        'info': 'The conversion from volts to statvolts.',
        'unit': '1',
        'type': float,
    },
}
"""Values and metadata for constants defined in `baseTypes.h`.

Each entry contains the numerical value (`'value'`), a brief description
(`'info'`), the metric unit (`'unit'`), and the built-in type (`'type'`) of each
defined constant.

Notes
-----
* A `'unit'` of `None` implies a non-physical parameter (e.g., a boolean flag or
  system path), whereas a `'unit'` of `'1'` implies a unitless physical
  parameter.

See Also
--------
`~runtime.Defaults`
    A mapping from parameter to default value, with value converted to its
    equivalent built-in type.

`~runtime.Interface`
    An aliased mapping from parameter to user-provided value, if available, or
    default value.
"""


CONFIGURATION_C = {
    'FailModeDump': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'adiabaticChangeAlg': {
        'type': int,
        'defaultVal': '1',
        'minVal': '1',
        'maxVal': '3',
        'aliases': [],
        'unit': None,
    },
    'adiabaticFocusAlg': {
        'type': int,
        'defaultVal': '1',
        'minVal': '1',
        'maxVal': '3',
        'aliases': [],
        'unit': None,
    },
    'aziSunStart': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'rad',
    },
    'boundaryFunctAmplitude': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['J0'],
        'unit': '1 / (cm^2 * s * sr * (MeV/nuc))',
    },
    'boundaryFunctBeta': {
        'type': float,
        'defaultVal': '2.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['beta'],
        'unit': '1',
    },
    'boundaryFunctEcutoff': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['E0'],
        'unit': 'MeV',
    },
    'boundaryFunctEr': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['Er', 'reference energy'],
        'unit': 'MeV',
    },
    'boundaryFunctGamma': {
        'type': float,
        'defaultVal': '2.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['gamma'],
        'unit': '1',
    },
    'boundaryFunctR0': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': 'config.rScale',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['R0', 'r0', 'reference radius'],
        'unit': 'au',
    },
    'boundaryFunctXi': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['xi'],
        'unit': '1',
    },
    'boundaryFunctionInitDomain': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'charge': {
        'type': list,
        'defaultVal': '[1.0]',
        'maxVal': 'LARGEFLOAT',
        'minVal': '1.0',
        'aliases': [],
        'unit': 'e',
    },
    'checkSeedPopulation': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'dsh_hel_min': {
        'type': float,
        'defaultVal': '2.5e-4',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
    },
    'dsh_min': {
        'type': float,
        'defaultVal': '5.0e-5',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
    },
    'dumpFreq': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1000000',
        'aliases': [],
        'unit': None,
    },
    'dumpOnAbort': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
    },
    'eMax': {
        'type': float,
        'defaultVal': '1000.0',
        'minVal': 'config.eMin',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'MeV/nuc',
    },
    'eMin': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'MeV/nuc',
    },
    'epCalcStartTime': {
        'type': float,
        'defaultVal': 'config.simStartTime',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'epEquilibriumCalcDuration': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'epremDomain': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'epremDomainOutputTime': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'fieldAligned': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
    },
    'flowMag': {
        'type': float,
        'defaultVal': '400.0e5',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'cm/s',
    },
    'fluxLimiter': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'focusingLimit': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': '0.0',
        'maxVal': '1.0',
    },
    'gammaEhigh': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '-1.0 * LARGEFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'gammaElow': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '-1.0 * LARGEFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'idealShock': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'idealShockFalloff': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': None,
    },
    'idealShockInitTime': {
        'type': float,
        'defaultVal': 'config.simStartTime',
        'minVal': 'config.simStartTime',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'idealShockJump': {
        'type': float,
        'defaultVal': '4.0',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'idealShockPhi': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'TWO_PI',
        'aliases': [],
        'unit': 'rad',
    },
    'idealShockPhiWidth': {
        'type': float,
        'defaultVal': 'config.idealShockWidth',
        'minVal': '0.0',
        'maxVal': 'PI',
        'aliases': [],
        'unit': 'rad',
    },
    'idealShockScale': {
        'type': float,
        'defaultVal': 'config.idealShockSharpness / config.idealShockScaleLength',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'au',
    },
    'idealShockScaleLength': {
        'type': float,
        'defaultVal': '0.0046491',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'au',
    },
    'idealShockSharpness': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'idealShockSpeed': {
        'type': float,
        'defaultVal': '1500e5',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'cm/s',
    },
    'idealShockTheta': {
        'type': float,
        'defaultVal': 'HALF_PI',
        'minVal': '0.0',
        'maxVal': 'PI',
        'aliases': [],
        'unit': 'rad',
    },
    'idealShockThetaWidth': {
        'type': float,
        'defaultVal': 'config.idealShockWidth',
        'minVal': '0.0',
        'maxVal': 'PI',
        'aliases': [],
        'unit': 'rad',
    },
    'idealShockWidth': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'PI',
        'aliases': [],
        'unit': 'rad',
    },
    'idw_p': {
        'type': float,
        'defaultVal': '3.0',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'kperxkpar': {
        'type': float,
        'defaultVal': '0.01',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['kper_kpar', 'kper/kpar', 'kper / kpar'],
        'unit': '1',
    },
    'lamo': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['lam0', 'lambda0'],
        'unit': 'au',
    },
    'mass': {
        'type': list,
        'defaultVal': '[1.0]',
        'maxVal': 'LARGEFLOAT',
        'minVal': '1.0',
        'aliases': [],
        'unit': 'nucleon',
    },
    'mfpRadialPower': {
        'type': float,
        'defaultVal': '2.0',
        'minVal': '-1.0 * LARGEFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['mfp_radial_power'],
        'unit': '1',
    },
    'mhdBAu': {
        'type': float,
        'defaultVal': '1.60e-5',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'G',
    },
    'mhdBConvert': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'mhdCouple': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'mhdCoupledTime': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'mhdDensityAu': {
        'type': float,
        'defaultVal': '8.30',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'cm^-3',
    },
    'mhdDigits': {
        'type': int,
        'defaultVal': '3',
        'minVal': '0',
        'maxVal': '32767',
        'aliases': [],
        'unit': None,
    },
    'mhdDirectory': {
        'type': str,
        'defaultVal': '',
        'aliases': [],
        'unit': None,
    },
    'mhdInitFromOuterBoundary': {
        'type': int,
        'defaultVal': '2',
        'minVal': '0',
        'maxVal': '2',
        'aliases': [],
        'unit': None,
    },
    'mhdInitMonteCarlo': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
    },
    'mhdInitRadius': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'au',
    },
    'mhdInitTimeStep': {
        'type': float,
        'defaultVal': '0.000011574074074',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'mhdNumFiles': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '32767',
        'aliases': [],
        'unit': None,
    },
    'mhdRadialMax': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'au',
    },
    'mhdRadialMin': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'au',
    },
    'mhdRhoConvert': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'mhdRotateSolution': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'mhdStartTime': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'mhdSteadyState': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'mhdTimeConvert': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'mhdVConvert': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'mhdVmin': {
        'type': float,
        'defaultVal': '50.0e5',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'cm/s',
    },
    'minInjectionEnergy': {
        'type': float,
        'defaultVal': '0.01',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'MeV',
    },
    'numColumnsPerFace': {
        'type': int,
        'defaultVal': '2',
        'minVal': '1',
        'maxVal': 'LARGEINT',
        'aliases': [],
        'unit': None,
    },
    'numEnergySteps': {
        'type': int,
        'defaultVal': '20',
        'minVal': '2',
        'maxVal': 'LARGEINT',
        'aliases': [],
        'unit': None,
    },
    'numEpSteps': {
        'type': int,
        'defaultVal': '30',
        'minVal': '1',
        'maxVal': 'LARGEINT',
        'aliases': [],
        'unit': None,
    },
    'numMuSteps': {
        'type': int,
        'defaultVal': '20',
        'minVal': '2',
        'maxVal': 'LARGEINT',
        'aliases': [],
        'unit': None,
    },
    'numNodesPerStream': {
        'type': int,
        'defaultVal': 'N_PROCS',
        'minVal': 'N_PROCS',
        'maxVal': 'LARGEINT',
        'aliases': [],
        'unit': None,
    },
    'numObservers': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1000',
        'aliases': [],
        'unit': '1',
    },
    'numRowsPerFace': {
        'type': int,
        'defaultVal': '2',
        'minVal': '1',
        'maxVal': 'LARGEINT',
        'aliases': [],
        'unit': None,
    },
    'numSpecies': {
        'type': int,
        'defaultVal': '1',
        'minVal': '1',
        'maxVal': '100',
        'aliases': [],
        'unit': None,
    },
    'obsPhi': {
        'type': list,
        'defaultVal': '[0.0]',
        'maxVal': 'TWO_PI',
        'minVal': '0.0',
        'aliases': [],
        'unit': 'rad',
    },
    'obsR': {
        'type': list,
        'defaultVal': '[config.rScale]',
        'maxVal': 'LARGEFLOAT',
        'minVal': 'config.rScale',
        'aliases': [],
        'unit': 'au',
    },
    'obsTheta': {
        'type': list,
        'defaultVal': '[0.0]',
        'maxVal': 'PI',
        'minVal': '0.0',
        'aliases': [],
        'unit': 'rad',
    },
    'omegaSun': {
        'type': float,
        'defaultVal': '0.001429813',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'rad * cm / (au * s)',
    },
    'outputFloat': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'outputRestart': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1000000',
    },
    'parallelFlow': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
    },
    'pointObserverOutput': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'pointObserverOutputTime': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'preEruptionDuration': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'rScale': {
        'type': float,
        'defaultVal': 'RSAU',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'au',
    },
    'rigidityPower': {
        'type': float,
        'defaultVal': 'third',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': ['rigidity_power'],
        'unit': '1',
    },
    'saveRestartFile': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
    },
    'seedFunctionTest': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
    },
    'shockDetectPercent': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'shockInjectionFactor': {
        'type': float,
        'defaultVal': '1.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': '1',
    },
    'shockSolver': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'simStartTime': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'simStopTime': {
        'type': float,
        'defaultVal': 'config.simStartTime + config.tDel',
        'minVal': 'config.simStartTime',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'streamFluxOutput': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'streamFluxOutputTime': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'streamSpawnLocAzi': {
        'type': list,
        'defaultVal': '[0.0]',
        'maxVal': 'TWO_PI',
        'minVal': '0.0',
        'aliases': [],
        'unit': 'rad',
    },
    'streamSpawnLocZen': {
        'type': list,
        'defaultVal': '[0.0]',
        'maxVal': 'PI',
        'minVal': '0.0',
        'aliases': [],
        'unit': 'rad',
    },
    'subTimeCouple': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'tDel': {
        'type': float,
        'defaultVal': '0.01041666666667',
        'minVal': 'SMALLFLOAT',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'unifiedOutput': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'unifiedOutputTime': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'unstructuredDomain': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'unstructuredDomainOutputTime': {
        'type': float,
        'defaultVal': '0.0',
        'minVal': '0.0',
        'maxVal': 'LARGEFLOAT',
        'aliases': [],
        'unit': 'day',
    },
    'useAdiabaticChange': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'useAdiabaticFocus': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'useBoundaryFunction': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
    },
    'useDegrees': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
    },
    'useDrift': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'useEPBoundary': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
    },
    'useManualStreamSpawnLoc': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'useMhdSteadyStateDt': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'useParallelDiffusion': {
        'type': int,
        'defaultVal': '1',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'useShellDiffusion': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
        'aliases': [],
        'unit': None,
    },
    'useStochastic': {
        'type': int,
        'defaultVal': '0',
        'minVal': '0',
        'maxVal': '1',
    },
    'warningsFile': {
        'type': str,
        'defaultVal': 'warningsXXX.txt',
        'aliases': [],
        'unit': None,
    },
}
"""Metadata for parameters defined in `configuration.c`.

Each entry contains the default value (`'default'`), the smallest acceptable
value ('`minimum`'), the largest acceptable value ('`maximum`'), as well as the
equivalent built-in type and metric unit of those values (`'type'` and
`'unit'`). Some entries also contain declared aliases for the parameter
('`aliases`').

Notes
-----
* This dictionary stores all values as strings because some values are defined
  with respect to others.
* A `'unit'` of `None` implies a non-physical parameter (e.g., a boolean flag or
  system path), whereas a `'unit'` of `'1'` implies a unitless physical
  parameter.

See Also
--------
`~runtime.Defaults`
    A mapping from parameter to default value, with value converted to its
    equivalent built-in type.

`~runtime.Interface`
    An aliased mapping from parameter to user-provided value, if available, or
    default value.
"""


