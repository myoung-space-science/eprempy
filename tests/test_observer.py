import itertools
import pathlib
import typing

import pytest

from eprempy import observable
from eprempy import observer
from eprempy import reference


@pytest.fixture
def streams(datadir: pathlib.Path) -> typing.Dict[str, observer.Stream]:
    """A collection of testable stream observers."""
    basedirs = {'isotropic-shock-with-dist', 'isotropic-shock-with-flux'}
    streams = {}
    for basedir in basedirs:
        source = datadir / basedir
        streams[source] = observer.stream_factory(0, 'eprem.cfg', source)
    return streams


UNOBSERVABLE = {'shell', 'shells', 'phiOffset'}
"""Quantities that tests should not try to observe."""


def test_init(streams: typing.Dict[str, observer.Stream]):
    """Test the ability to initialize the observer interface."""
    for stream in streams.values():
        names = set(reference.ARRAYS.names) - UNOBSERVABLE
        for name in names:
            assert isinstance(stream[name], observable.Quantity)


def test_observer_as_mapping(streams: typing.Dict[str, observer.Stream]):
    """Test the observer's mapping-like interface."""
    for stream in streams.values():
        observables = stream.observables
        parameters = stream.parameters
        assert len(stream) == len(observables) + len(parameters)
        assert tuple(stream) == tuple(observables) + tuple(parameters)
        r_keys = ('r', 'R', 'radius')
        for key in r_keys:
            assert key in stream
            assert key in stream.observables
            assert key not in stream.parameters
        mfp_keys = ('mfp', 'mean free path', 'mean_free_path')
        for key in mfp_keys:
            assert key in stream
            assert key in stream.observables
            assert key not in stream.parameters
        for ki, kj in itertools.product(r_keys, mfp_keys):
            key = f"{ki.replace(' ', '_')} / {kj.replace(' ', '_')}"
            assert key in stream
            assert key in stream.observables
            assert key not in stream.parameters
        for key in ('lamo', 'lam0', 'lambda0'):
            assert key in stream
            assert key in stream.parameters
            assert key not in stream.observables


def test_observable_aliases(streams: typing.Dict[str, observer.Stream]):
    """Make sure the user can access quantities by known aliases."""
    observables = reference.OBSERVABLES.names.values(aliased=True)
    names = set(observables) - UNOBSERVABLE
    for stream in streams.values():
        for name in names:
            aliases = reference.OBSERVABLES.aliases[name]
            for alias in aliases:
                assert stream[name] == stream[alias]
