"""
Support for objects that manage numeric data.
"""

import numbers
import typing

import numpy.typing

from . import _data as data
from . import _operators as operators
from . import _implementation as implementation
from . import _index as index
from . import _factory as factory
from ._array import (
    Array,
    array_factory as array,
    Dimensions,
    dimensions_factory as dimensions,
    remesh,
)
from ._operations import (
    _OPERATIONS as OPERATIONS,
    _OPERATORS as OPERATORS,
    IMPLEMENTATIONS,
    FUNCTIONS,
    METHODS,
    DUNDER,
    CALLABLES,
    OperandTypeError,
)
from ._mixins import (
    Functions,
    Operators,
)
from ._objects import (
    Quantity,
    Interface,
    Object,
    Type,
)

# HACK: This should be in the public namespace.
from ._implementation import Result

# HACK: Define this to avoid import errors until full deprecation.
Implementation = object


__all__ = [
    'array',
    'data',
    'dimensions',
    'implementation',
    'index',
    'operators',
    'remesh',
    'factory',
    'Functions',
    'Operators',
    'Array',
    'Dimensions',
    'Quantity',
    'Interface',
    'Object',
    'OperandTypeError',
    'Result',
    'Type',
    'CALLABLES',
    'DUNDER',
    'FUNCTIONS',
    'IMPLEMENTATIONS',
    'METHODS',
    'OPERATIONS',
    'OPERATORS',
]


@typing.runtime_checkable
class ArrayType(typing.Protocol):
    """Structural protocol for numeric arrays."""

    @property
    def dimensions(self) -> Dimensions: ...

    @property
    def array(self) -> numpy.typing.NDArray: ...

    @property
    def shapemap(self) -> typing.Dict[str, int]: ...

    @property
    def shape(self) -> typing.Tuple[int, ...]: ...


ArrayLike = typing.Union[
    numpy.typing.NDArray[numpy.number],
    typing.Sequence[numbers.Number],
]
"""Type alias for array-like numeric objects."""
# TODO: Include nested sequences.


