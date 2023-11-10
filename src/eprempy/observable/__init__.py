"""
Support for working with observable EPREM quantities.
"""

import typing

from .. import metric
from .. import paths
from ._objects import (
    Array,
    Quantity,
)
from ._interfaces import Quantities

__all__ = [
    'Array',
    'Quantities',
    'Quantity',
    'quantities',
]


def quantities(
    source: paths.PathLike,
    config: paths.PathLike,
    system: typing.Optional[str]=None,
) -> Quantities:
    """Create a collection of observable arrays."""
    return Quantities(
        paths.fullpath(source, strict=True),
        paths.fullpath(config, strict=True),
        system=metric.system(system or 'mks')
    )


