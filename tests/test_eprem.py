"""
Tests of the top-level API.
"""

import pathlib
import typing

import numpy
import pytest

from eprempy import (
    eprem,
    physical,
    reference,
    Array,
    Observable,
)


# TODO
# - interpolation
# - access arbitrary parameter
# - physical assumptions have correct unit


UNOBSERVABLE = {'shell', 'shells', 'phiOffset'}
"""Quantities that tests should not try to observe."""


@pytest.fixture
def streams(datadir: pathlib.Path) -> typing.Dict[str, eprem.Stream]:
    """A collection of testable stream-observer interfaces."""
    basedirs = {'isotropic-shock-with-dist', 'isotropic-shock-with-flux'}
    observers = {}
    for basedir in basedirs:
        source = datadir / basedir
        observers[source] = eprem.stream(0, 'eprem.cfg', source)
    return observers


@pytest.fixture
def points(datadir: pathlib.Path) -> typing.Dict[str, eprem.Stream]:
    """A collection of testable point-observer interfaces."""
    basedirs = {'isotropic-shock-with-dist', 'isotropic-shock-with-flux'}
    observers = {}
    for basedir in basedirs:
        source = datadir / basedir
        observers[source] = eprem.point('000', 'eprem.cfg', source)
    return observers


def test_observer_mapping(streams: typing.Dict[str, eprem.Stream]):
    """Test the ability to access observable quantities."""
    names = set(reference.ARRAYS.names) - UNOBSERVABLE
    for stream in streams.values():
        for name in names:
            assert isinstance(stream[name], Observable)
    observables = reference.OBSERVABLES.names.values(aliased=True)
    names = set(observables) - UNOBSERVABLE
    for stream in streams.values():
        for name in names:
            aliases = reference.OBSERVABLES.aliases[name]
            for alias in aliases:
                assert stream[name] == stream[alias]


def test_observer_axes(streams: typing.Dict[str, eprem.Stream]):
    """Test the observer axis-based properties."""
    for stream in streams.values():
        assert isinstance(stream.times, physical.Coordinates)
        assert numpy.array_equal(stream.times.data, stream['time'])
        assert isinstance(stream.shells, physical.Points)
        shells = numpy.arange(len(stream.shells))
        assert numpy.array_equal(stream.shells.data, shells)
        assert isinstance(stream.species, physical.Symbols)
        assert list(stream.species) == ['H+']
        assert isinstance(stream.energies, physical.Coordinates)
        assert numpy.array_equal(stream.energies.data, stream['energy'])
        assert isinstance(stream.mus, physical.Coordinates)
        assert numpy.array_equal(stream.mus.data, stream['mu'])


def test_observer_hash(datadir: pathlib.Path):
    """Test the ability to hash an observer."""
    basedirs = {'isotropic-shock-with-dist', 'isotropic-shock-with-flux'}
    for basedir in basedirs:
        source = datadir / basedir
        for n in (0, 4):
            stream = eprem.stream(n, 'eprem.cfg', source)
            assert hash(stream)


def test_create_dataset(datadir: pathlib.Path, datasets: dict):
    """Create an interface to a complete dataset."""
    observables = reference.OBSERVABLES.names.values(aliased=True)
    names = set(observables) - UNOBSERVABLE
    for filename in datasets:
        for system in ('mks', 'cgs'):
            source = datadir / filename
            dataset = eprem.dataset(source, config='eprem.cfg', system=system)
            assert isinstance(dataset, eprem.Dataset)
            assert dataset.directory == source
            assert dataset.system == system
            for observer in dataset.observers.values():
                for name in names:
                    aliases = reference.OBSERVABLES.aliases[name]
                    for alias in aliases:
                        assert observer[name] == observer[alias]
            for stream in dataset.streams.values():
                assert isinstance(stream, eprem.Stream)
            for point in dataset.points.values():
                assert isinstance(point, eprem.Point)


def test_symbolic_species(datadir: pathlib.Path):
    """Subscript the species axis with a valid chemical symbol."""
    source = datadir / 'isotropic-shock-with-flux'
    config = 'eprem.cfg'
    stream = eprem.stream(0, config, source)
    flux = stream['flux'][0, 0, 'H+', 0]
    assert isinstance(flux, Array)
    with pytest.raises(ValueError):
        stream['flux'][0, 0, '!@', 0]


def test_observable_array(datadir: pathlib.Path):
    """Directly convert an observable quantity into an array."""
    source = datadir / 'isotropic-shock-with-flux'
    config = 'eprem.cfg'
    stream = eprem.stream(0, config, source)
    mfp = stream['mfp']
    ndarray = numpy.array(mfp)
    assert isinstance(ndarray, numpy.ndarray)
    array = mfp[:]
    assert isinstance(array, Array)
    assert ndarray.shape == array.shape


def test_observable_algebra(datadir: pathlib.Path):
    """Algebraically create an observable quantity."""
    source = datadir / 'isotropic-shock-with-flux'
    config = 'eprem.cfg'
    stream = eprem.stream(0, config, source)
    mfp = stream['mfp']
    mfp_sqr = mfp ** 2
    assert isinstance(mfp_sqr, Observable)
    assert mfp_sqr.unit == mfp.unit**2
    assert mfp_sqr.dimensions == mfp.dimensions
    ur = stream['ur']
    mfp_ur = mfp / ur
    assert isinstance(mfp_ur, Observable)
    assert mfp_ur.unit == mfp.unit / ur.unit
    assert mfp_ur.dimensions == mfp.dimensions | ur.dimensions
    mfpxur = mfp * ur
    assert isinstance(mfpxur, Observable)
    assert mfpxur.unit == mfp.unit * ur.unit
    assert mfpxur.dimensions == mfp.dimensions | ur.dimensions
    with pytest.raises(ValueError):
        mfp + ur
    with pytest.raises(ValueError):
        mfp - ur
    utheta = stream['utheta']
    utheta_plus_ur = utheta + ur
    assert isinstance(utheta_plus_ur, Observable)
    assert utheta_plus_ur.unit == ur.unit
    assert utheta_plus_ur.dimensions == ur.dimensions
    utheta_minus_ur = utheta - ur
    assert isinstance(utheta_minus_ur, Observable)
    assert utheta_minus_ur.unit == ur.unit
    assert utheta_minus_ur.dimensions == ur.dimensions
    ur_utheta = ur / utheta
    combined = ur_utheta * mfp_sqr
    assert isinstance(combined, Observable)
    assert combined.unit == ur_utheta.unit * mfp_sqr.unit
    assert combined.dimensions == mfp.dimensions | ur_utheta.dimensions


def test_symbolic_observable(datadir: pathlib.Path):
    """Symbolically create an observable quantity."""
    source = datadir / 'isotropic-shock-with-flux'
    config = 'eprem.cfg'
    stream = eprem.stream(0, config, source)
    mfp = stream['mfp']
    mfp_sqr = stream['mfp**2']
    assert isinstance(mfp_sqr, Observable)
    assert mfp_sqr.unit == mfp.unit**2
    assert mfp_sqr.dimensions == mfp.dimensions
    ur = stream['ur']
    mfp_ur = stream['mfp / ur']
    assert isinstance(mfp_ur, Observable)
    assert mfp_ur.unit == mfp.unit / ur.unit
    assert mfp_ur.dimensions == mfp.dimensions | ur.dimensions
    mfpxur = stream['mfp * ur']
    assert isinstance(mfpxur, Observable)
    assert mfpxur.unit == mfp.unit * ur.unit
    assert mfpxur.dimensions == mfp.dimensions | ur.dimensions
    with pytest.raises(KeyError):
        stream['mfp / lambda0']


def test_radial_interpolation(datadir: pathlib.Path) -> None:
    """Interpolate integral flux to radial values."""
    source = datadir / 'isotropic-shock-with-flux'
    config = 'eprem.cfg'
    stream = eprem.stream(0, config, source)
    indices = (40, (1.0, 'au'), (1.5e11, 'm'))
    shape = (50, 1, 1, 1)
    unit = 'cm^-2 s^-1 sr^-1'
    minenergy = (10.0, 'MeV')
    for index in indices:
        if isinstance(index, int):
            dimensions = ('time', 'shell', 'species', 'minimum energy')
        else:
            dimensions = ('time', 'radius', 'species', 'minimum energy')
        observed = stream['integral flux'][:, index, 'H+', minenergy]
        converted = observed.withunit(unit)
        assert converted.shape == shape
        assert converted.dimensions == dimensions
        assert converted.unit == unit


def test_fluence_subscription(datadir: pathlib.Path) -> None:
    """Fluence should always have a single time point."""
    source = datadir / 'isotropic-shock-with-flux'
    config = 'eprem.cfg'
    stream = eprem.stream(0, config, source)
    fluence = stream['fluence']
    shape = numpy.array(fluence).shape
    times = (
        0,
        1,
        -1,
        range(4),
        range(2, 10),
        slice(4),
        slice(2, 10),
        slice(None),
        (3, 'hour'),
    )
    for time in times:
        array = fluence[time, ...]
        assert array.shape == (1, *shape[1:])

