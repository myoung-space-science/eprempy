# EPREM(py)

Tools for working with EPREM simulation runs

## Installation

```bash
$ pip install eprempy
```

## Usage

Before getting started in earnest with `eprempy`, one simple task you can perform to make sure everything is installed is to print the version number.

```python
>>> import eprempy
>>> print(eprempy.__version__)
```

You can also print the version number via the package command-line interface (CLI)

```shell
$ python -m eprempy --version
```

The value printed will depend on which version you have installed.

### Dataset interfaces

The examples below assume a working knowledge of [EPREM](https://github.com/myoung-space-science/eprem) &mdash; essentially, they assume that you have successfully run EPREM and have access to both the runtime configuration file and the output files.

Most users will begin by creating an interface to a full dataset, or to a single stream or point observer. The syntax is similar among all three cases.

You may create an interface to a full dataset by providing a path to the directory containing output from an EPREM simulation run (`source`), the name of the runtime configuration file used to initialize the simulation run (`config`), and the metric system in which to observe physical quantities (`system`).

```python
from eprempy import eprem

dataset = eprem.dataset(source='/path/to/my/eprem/run', config='eprem.cfg', system='mks')
```

All parameters have default values

* The default `source` is the current directory.
* The default `config` is any file called `eprem_input_file`, or a file ending in `.cfg`, `.ini`, or `.in`.
* The default `system` is `'mks'` &mdash; options are `'mks'` or `'cgs'` (case-insensitive).

Each dataset has the following properties

* `directory`: the full path to the relevant EPREM output directory.
* `config`: the full path to the runtime configuration file used to initialize the EPREM simulation run.
* `system`: an instance of `eprempy.metric.System` representing an observer's metric system
* `observers`: all observers in the dataset, keyed by ID.
* `streams`: all stream observers in the dataset, keyed by ID.
* `points`: all point observers in the dataset, keyed by ID.
* `parameters`: an interface to EPREM runtime parameter values.

### Observer interfaces

You may directly create an individual observer by providing its ID (e.g., stream number or name), as well as the same arguments used to create a dataset. The observer ID must be the first argument and is required.

```python
from eprempy import eprem

stream = eprem.stream(4, source='/path/to/my/eprem/run', config='eprem.cfg', system='mks')
point = eprem.point(1, source='/path/to/my/eprem/run', config='eprem.cfg', system='mks')
```

A stream-observer ID is alway an integer. A point-observer ID may be a string or an integer, in order to accommodate the possibility of named point observers (e.g., 'earth' or 'PSP') in EPREM.

Therefore, the following invokations are equivalent to those above, as long as you're working in the simulation output directory and the simulation configuration file has a standard name.

```python
from eprempy import eprem

dataset = eprem.dataset()
stream = eprem.stream(4)
point = eprem.point(1)
```

Each observer has the following properties

* `source`: the full path to an observer's data file.
* `system`: an instance of `eprempy.metric.System` representing an observer's metric system.
* `times`: the observer's time coordinates.
* `species`: the available particle species.

### Observable quantities

Every observer provides a key-based interface (i.e., a mapping) to observable quantities. Users may request a known observable quantity from an observer by passing a valid alias for the observable via bracket syntax. For example, any of the following commands will return the observable quantity representing particle flux

```python
stream['flux']
stream['Flux']
stream['j']
stream['J']
```

Each observable quantity knows its unit and its subscriptable dimensions.

```python
>>> stream = eprem.stream(4, system='mks')
>>> stream['flux']
Quantity(unit='J^-1 s^-1 sr^-1 m^-2', dimensions={'time', 'shell', 'species', 'energy'})
>>> stream = eprem.stream(4, system='cgs')
>>> stream['flux']
Quantity(unit='erg^-1 s^-1 sr^-1 cm^-2', dimensions={'time', 'shell', 'species', 'energy'})
```

An observable quantity has `unit` and `dimensions` properties. Using the MKS example,

```python
>>> flux = stream['flux']
>>> flux.unit
Unit('J^-1 s^-1 sr^-1 m^-2')
>>> flux.dimensions
Dimensions({'time', 'shell', 'species', 'energy'})
```

It is possible to change the unit of an observable quantity via the `.withunit` method.

```python
>>> stream['flux'].withunit('1 / (cm^2 s sr MeV/nuc)')
Quantity(unit='nuc MeV^-1 s^-1 sr^-1 cm^-2', dimensions={'time', 'shell', 'species', 'energy'})
```

The full list of observable quantities, with registered aliases, is

* 'phiOffset'
* 't' = 'times' = 'time'
* 'shells' = 'shell'
* 'pitch-angle cosines' = 'mu' = 'pitch-angle cosine' = 'pitch-angle' = 'pitch angles' = 'pitch angle' = 'pitch-angles'
* 'm' = 'mass'
* 'q' = 'charge'
* 'energy' = 'egrid' = 'E' = 'energies'
* 'v' = 'vgrid' = 'speed'
* 'radius' = 'R' = 'r'
* 'T' = 'theta'
* 'phi' = 'P'
* 'Br' = 'br'
* 'bt' = 'btheta' = 'Btheta' = 'Bt'
* 'Bphi' = 'Bp' = 'bphi' = 'bp'
* 'ur' = 'vr' = 'Vr' = 'Ur'
* 'Ut' = 'utheta' = 'Utheta' = 'Vtheta' = 'Vt' = 'ut'
* 'uphi' = 'up' = 'Vp' = 'Vphi' = 'Up' = 'Uphi'
* 'rho' = 'Rho'
* 'Dist' = 'dist' = 'f'
* 'Flux' = 'J' = 'j(E)' = 'j' = 'J(E)' = 'flux'
* 'X' = 'x'
* 'y' = 'Y'
* 'Z' = 'z'
* 'bmag' = 'b_mag' = 'b mag' = '|b|' = '|B|' = 'b' = 'B'
* 'u mag' = 'umag' = '|U|' = 'U' = 'u_mag' = 'u' = '|u|'
* 'Upara' = 'u_para' = 'upara'
* 'u_perp' = 'Uperp' = 'uperp'
* 'angle' = 'flow_angle' = 'flow angle'
* 'div_u' = 'divu' = 'div(u)' = 'div(U)' = 'divU' = 'div u' = 'div U'
* 'Rg' = 'rigidity' = 'R_g'
* 'mean_free_path' = 'mean free path' = 'mfp'
* 'ar' = 'acceleration rate' = 'acceleration_rate'
* 'energy_density' = 'energy density'
* 'average_energy' = 'average energy'
* 'fluence'
* 'integral flux' = 'integral_flux' = 'intflux'

### Observations

Users may observe an observable quantity via standard subscription syntax, such as

```python
flux[0, 0, 0, 0]
flux[0, ...]
flux[:, 0, ...]
flux[:]
```

Users may also observe an observable quantity via physical subscription syntax, such as

```python
time = 1.0, 2.0, 'day'
radius = 0.5, 'au'
species = 'H+'
energy = 1.0, 10.0, 100.0, 'MeV'
flux[time, radius, species, energy]
```
or, more compactly,
```python
flux[(1.0, 2.0, 'day'), (0.5, 'au'), 'H+', (1.0, 10.0, 100.0, 'MeV')]
```

Note that physical subscription syntax requires a tuple to express an index with one or more value(s) and a unit.

Each observation inherits its unit from the observable quantity at the time of observation, and it has its own `unit` property and `withunit` method. In place of the `dimensions` property, each observation has an `axes` property that contains information about the specific axis types and their corresponding values.

Changing an observation's unit self-consistently scales the observed values. Attempting to convert an observable quantity or an observation to a physically inconsistent unit (e.g., converting 'm / s' to 'kg / erg') raises a `ValueError`.

You may directly convert any observation to a `numpy.ndarray`

```python
import numpy

numpy.array(flux[0, 0, 0, 0])
numpy.array(flux[:])
```

You may also directly convert any observable quantity to a `numpy.ndarray`

```python
numpy.array(flux)
```
Doing so is essentially a shortcut for converting the full observation.

### Runtime parameters

Accessing a runtime parameter value via the dataset interface's `parameters` property returns a `Variable` for physical quantities &mdash; those with one or more value(s) and a unit &mdash; and a built-in type (e.g., integer or string) for all other quantities.

The full list of parameters, with registered aliases, is

* 'FailModeDump'
* 'adiabaticChangeAlg'
* 'adiabaticFocusAlg'
* 'aziSunStart'
* 'boundaryFunctAmplitude' = 'J0'
* 'boundaryFunctBeta' = 'beta'
* 'E0' = 'boundaryFunctEcutoff'
* 'reference energy' = 'boundaryFunctEr' = 'Er'
* 'gamma' = 'boundaryFunctGamma'
* 'reference radius' = 'R0' = 'boundaryFunctR0' = 'r0'
* 'boundaryFunctXi' = 'xi'
* 'boundaryFunctionInitDomain'
* 'charge'
* 'checkSeedPopulation'
* 'dsh_hel_min'
* 'dsh_min'
* 'dumpFreq'
* 'dumpOnAbort'
* 'eMax'
* 'eMin'
* 'epCalcStartTime'
* 'epEquilibriumCalcDuration'
* 'epremDomain'
* 'epremDomainOutputTime'
* 'fieldAligned'
* 'flowMag'
* 'fluxLimiter'
* 'focusingLimit'
* 'gammaEhigh'
* 'gammaElow'
* 'idealShock'
* 'idealShockFalloff'
* 'idealShockInitTime'
* 'idealShockJump'
* 'idealShockPhi'
* 'idealShockPhiWidth'
* 'idealShockScale'
* 'idealShockScaleLength'
* 'idealShockSharpness'
* 'idealShockSpeed'
* 'idealShockTheta'
* 'idealShockThetaWidth'
* 'idealShockWidth'
* 'idw_p'
* 'kper/kpar' = 'kperxkpar' = 'kper / kpar' = 'kper_kpar'
* 'lambda0' = 'lam0' = 'lamo'
* 'mass'
* 'mfpRadialPower' = 'mfp_radial_power'
* 'mhdBAu'
* 'mhdBConvert'
* 'mhdCouple'
* 'mhdCoupledTime'
* 'mhdDensityAu'
* 'mhdDigits'
* 'mhdDirectory'
* 'mhdInitFromOuterBoundary'
* 'mhdInitMonteCarlo'
* 'mhdInitRadius'
* 'mhdInitTimeStep'
* 'mhdNumFiles'
* 'mhdRadialMax'
* 'mhdRadialMin'
* 'mhdRhoConvert'
* 'mhdRotateSolution'
* 'mhdStartTime'
* 'mhdSteadyState'
* 'mhdTimeConvert'
* 'mhdVConvert'
* 'mhdVmin'
* 'minInjectionEnergy'
* 'numColumnsPerFace'
* 'numEnergySteps'
* 'numEpSteps'
* 'numMuSteps'
* 'numNodesPerStream'
* 'numObservers'
* 'numRowsPerFace'
* 'numSpecies'
* 'obsPhi'
* 'obsR'
* 'obsTheta'
* 'omegaSun'
* 'outputFloat'
* 'outputRestart'
* 'parallelFlow'
* 'pointObserverOutput'
* 'pointObserverOutputTime'
* 'preEruptionDuration'
* 'rScale'
* 'rigidityPower' = 'rigidity_power'
* 'saveRestartFile'
* 'seedFunctionTest'
* 'shockDetectPercent'
* 'shockInjectionFactor'
* 'shockSolver'
* 'simStartTime'
* 'simStopTime'
* 'streamFluxOutput'
* 'streamFluxOutputTime'
* 'streamSpawnLocAzi'
* 'streamSpawnLocZen'
* 'subTimeCouple'
* 'tDel'
* 'unifiedOutput'
* 'unifiedOutputTime'
* 'unstructuredDomain'
* 'unstructuredDomainOutputTime'
* 'useAdiabaticChange'
* 'useAdiabaticFocus'
* 'useBoundaryFunction'
* 'useDegrees'
* 'useDrift'
* 'useEPBoundary'
* 'useManualStreamSpawnLoc'
* 'useMhdSteadyStateDt'
* 'useParallelDiffusion'
* 'useShellDiffusion'
* 'useStochastic'
* 'warningsFile'

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`eprempy` was created by Matt Young. It is licensed under the terms of the BSD 3-Clause license.

## Credits

`eprempy` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
