<!-- Note to developers: version subheadings should have the form vX.Y.Z (YYYY-MM-DD) -->

# Changelog

## NEXT

## v0.6.0 (2024-05-31)

- Add `stream` and `point` to known observer-file prefixes

## v0.5.5 (2024-05-29)

- Fix `measured.Value` bug in `physical.Coordinates.index`

## v0.5.4 (2024-03-27)

- Add `eprem.BASETYPES`
- Add `eprem.PARAMETERS`
- Add `eprem.OBSERVABLES`
- Update example usage in `README.md`
- Fix bug in `eprem.Dataset` instantiation
- Update string representation of `physical.Coordinates` and `eprem.Dataset`

## v0.5.3 (2024-02-21)

- Update type annotations
- Fix bug in `physical.Coordinates.index` to allow `quantity.Measurement`

## v0.5.2 (2024-02-16)

- Fix config-file parsing bug
- Improve CLI config-file diff output
- Add test for CLI config-file diff option

## v0.5.1 (2024-02-09)

- Fix multiple bugs in package CLI

## v0.5.0 (2024-02-09)

- Support length conversions to/from solar radius
- Reorganize the package CLI
- Create `scripts/default-parameters.py`
- Refactor the `parameter` namespace

## v0.4.0 (2024-01-31)

- Extend observable coordinate subscription to support "interpolated" values
- Implement `numpy` logarithmic universal functions on physical objects
- Improve quantity parsing and measuring

## v0.3.8 (2024-01-29)

- Fix subscription bugs in `real.Array` and `physical.Array`

## v0.3.7 (2024-01-26)

- Extract `atomic.py` from `universal.py`
- Define `atomic.Species` and `atomic.species`
- Make point-observer coordinates more precise

## v0.3.6 (2024-01-24)

- Fix bugs in config-parameter parsing and update default values

## v0.3.5 (2024-01-23)

- Implement `numpy.trapz` for real and physical array-like objects
- Support additive and multiplicative operations between physical scalars and measurable tuples
- Support additive and multiplicative operations between physical vectors and measurable tuples

## v0.3.4 (2024-01-22)

- Improve indexing of `physical.Array`
- Consistently handle `keepdims` in the overloaded implementation of `numpy.sum`

## v0.3.3 (2024-01-19)

- Improve robustness of metric unit conversions
- Include geometric factor in unit of flux (and derived quantities)
- Add unit-conversion test cases

## v0.3.2 (2024-01-18)

- Define `eprem.Stream` and `eprem.Point` subclasses of `eprem.Observer`
- Define `streams` and `points` properties of `eprem.Dataset`
- Skip non-data type files when creating `eprem.Dataset` observer properties
- Force test-runner script to stop on first error and support pass-through arguments
- Expand observer tests
- Update test fixtures

## v0.3.1 (2024-01-17)

- Fix bugs in dataset and observer interfaces

## v0.3.0 (2024-01-17)

- Create `eprem.Dataset`: interface to a complete set of simulation output
- Refactor observer interfaces
- Add test to keep `import *` up-to-date
- Rename `dataset` namespace to `datafile`

## v0.2.0 (2023-12-20)

- Fix bugs in `physical.Array` plotting
- Make observers hashable

## v0.1.11 (2023-12-06)

- Allow measurable objects with numeric strings to be unitless
- Allow a single numeric string to be measurable
- Fix bug in `quantity.measure` for `measured.Object` input

## v0.1.10 (2023-12-06)

- Support casting instances of `physical.Array` to built-in numeric types
- Remove superfluous (and potentially misleading) operators from `physical.Axes`
- Remove superfluous `reference` property from `physical.Axes`
- Allow measurable objects to have numeric string values

## v0.1.9 (2023-11-30)

- Update README Usage
- Fix CLI bug

## v0.1.8 (2023-11-29)

- Define observer axes properties
- Add '-V/--verbose' option to CLI
- Print informative message when CLI called without arguments

## v0.1.7 (2023-11-29)

- Update formatting of length-1 measured objects when using parameter compare CLI
- Define `Observer.source` property
- Create examples/cli.md document
- Make aliased observable quantities equal
- Define `dataset.Arrays.hasdist` property

## v0.1.6 (2023-11-28)

- Define `physical.Axis.__contains__`
- Define `physical.Axes.__add__`
- Improve broadcasting support in array additive operations

## v0.1.5 (2023-11-27)

- Add package CLI with parameter-based modes
- Expose `compare` and `generate` functions from parameter namespace

## v0.1.4 (2023-11-17)

- Refactor `symbolic.Expression.format`
- Define `Observer.which` method

## v0.1.3 (2023-11-15)

- Fix bug in observable interpolation
- Edit README Usage

## v0.1.2 (2023-11-14)

- Rename `ConfigFile.filepath` to `.source`
- Add project development dependency: Python Semantic Release
- Develop examples for **Usage** section of README

## v0.1.1 (2023-11-13)

- Fix backwards-compatibility (to Python 3.9) of type annotations

## v0.1.0 (2023-11-09)

- First release of `eprempy`!
