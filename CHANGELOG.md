<!-- Note to developers: version subheadings should have the form vX.Y.Z (YYYY-MM-DD) -->

# Changelog

## NEXT

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
