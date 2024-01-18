"""
Support for reading data and metadata from EPREM observer files.
"""

import typing

from ._core import (
    Array,
    Scalar,
    Axis,
    array_factory as array,
    scalar_factory as scalar,
    axis_factory as axis,
)
from ._reference import (
    ARRAYS,
    SCALARS,
    AXES,
)
from ._viewers import (
    HINTS,
    VIEWERS,
    View,
    view_factory as view,
)
from ._interfaces import (
    Axes,
    Arrays,
    Grid,
    axes_factory as axes,
    arrays_factory as arrays,
    grid_factory as grid,
)


Observable = typing.Union[Array, Scalar]
Member = typing.Union[Array, Scalar, Axes]


__all__ = [
    'ARRAYS',
    'SCALARS',
    'AXES',
    'HINTS',
    'VIEWERS',
    'Array',
    'Scalar',
    'Axis',
    'View',
    'Axes',
    'Arrays',
    'Grid',
    'array',
    'scalar',
    'axis',
    'view',
    'axes',
    'arrays',
    'grid',
]


