"""
Tests of the top-level API.
"""

import pathlib

import numpy
import pytest

from eprempy import (
    eprem,
    Array,
    Observable,
)


# TODO
# - interpolation
# - access arbitrary parameter
# - physical assumptions have correct unit


def test_create_dataset(datadir: pathlib.Path):
    """Create an interface to a complete dataset."""
    source = datadir / 'isotropic-shock-with-flux'
    dataset = eprem.dataset(source, config='eprem.cfg')
    assert isinstance(dataset, eprem.Dataset)
    assert dataset.directory == source
    assert dataset.system == 'mks'


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
    lambda0 = stream['lambda0']
    with pytest.raises(TypeError):
        mfp / lambda0
    mfp_l0 = mfp[:] / lambda0
    assert isinstance(mfp_l0, Array)
    assert mfp_l0.unit == mfp.unit / lambda0.unit
    assert mfp_l0.dimensions == mfp.dimensions


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

