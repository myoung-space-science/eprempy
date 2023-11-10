"""
Support for creating interfaces to EPREM observers
"""


import typing

from .. import paths
from . import _objects


__all__ = [
    'Stream',
    'Point',
    'stream_factory',
    'point_factory',
]


# NOTE: The individual classes and factories for streams and points are
# currently simple wrappers around their respective generic-observer objects.
# This is syntactic sugar for now, but the distinction will be useful if we
# decide to functionally distinguish the two observer types in the future.


class Stream(_objects.Observer): ...


def stream_factory(
    __id: typing.Union[str, int],
    config: paths.PathLike=None,
    source: paths.PathLike=None,
    system: str=None,
) -> _objects.Observer:
    """Create an EPREM stream observer."""
    return _objects.factory(__id, config, source, system)


class Point(_objects.Observer): ...


def point_factory(
    __id: typing.Union[str, int],
    config: paths.PathLike=None,
    source: paths.PathLike=None,
    system: str=None,
) -> _objects.Observer:
    """Create an EPREM point observer."""
    return _objects.factory(__id, config, source, system)


