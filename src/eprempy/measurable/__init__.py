"""
Support for defining and working with measurable objects.
"""

import numbers
import typing

import numpy
import numpy.typing

from .. import metric


@typing.runtime_checkable
class Type(metric.Type, typing.Protocol):
    """Structural protocol class for metric objects with data."""

    data: typing.Union[
        typing.Sequence[numbers.Real],
        numpy.typing.NDArray[numpy.integer],
        numpy.typing.NDArray[numpy.floating],
    ]


