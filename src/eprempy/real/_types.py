import numbers
import typing

import numpy
import numpy.typing


ValueType = typing.TypeVar('ValueType', int, float, numbers.Real)
"""Type variable representing real numeric values.

This type variable is constrained to be one of the following standard types

- `int`
- `float`
- `numbers.Real`
"""


# NOTE: These are a WIP attempt to define a generic type variable that
# represents either
# - a single real value
# - an array of arbitrary depth that contains real values
_T = typing.TypeVar('_T')
_NestedSequence = typing.Union[
    typing.Sequence[_T],
    typing.Sequence["_NestedSequence[_T]"],
]
DataType = typing.Union[
    ValueType,
    _NestedSequence[ValueType],
    numpy.typing.ArrayLike,
]


