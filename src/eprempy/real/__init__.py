"""
Support for numeric objects with real-valued data.
"""

import numbers
import typing

import numpy.typing

from .. import base
from .. import container
from ._types import ValueType
from ._objects import (
    Variable,
)
from ._array import (
    Array,
    array_factory as array,
)


__all__ = [
    'Array',
    'ValueType',
    'Variable',
    'array',
]


ArrayLike = typing.Union[
    numpy.typing.NDArray[numpy.integer],
    numpy.typing.NDArray[numpy.floating],
    typing.Sequence[numbers.Real],
]
"""Type alias for array-like objects with real-valued data."""
# TODO: Include nested sequences.


def variable(
    x: typing.Union[ValueType, typing.Sequence[ValueType]],
    /,
) -> Variable[ValueType]:
    """Create a real-valued variable.
    
    Parameters
    ----------
    x : real number or sequence of real numbers
        The real-valued object from which to create a new variable.

    Returns
    -------
    `~Variable`

    Raises
    ------
    `TypeError`
        The caller passed a single object of non-numeric type or a sequence that
        includes members of non-numeric type.
    """
    if container.isseparable(x):
        if all(base.isreal(v) for v in x):
            return Variable(x)
        raise TypeError(
            f"Cannot create a variable from {x!r}"
            " with non-numeric values."
        )
    if not base.isreal(x):
        raise TypeError(
            f"Cannot create variable from object of type {type(x)}"
        ) from None
    return Variable([x])


class Template(base.abc.Real):
    """Abstract class template for a real-valued object.
    
    The body of this class definition simply defines each real-valued operator
    (i.e., an operator required by the real-valued protocol) by reference to the
    corresponding abstract method on `~base.abc.Real`.This class is therefore
    isomorphic to `~base.abc.Real`. It exists to serve as a template for copying
    method placeholders to a concrete implementation of the real-valued
    protocol.

    See Also
    --------
    `~base.Real`
        Definition of the real-valued protocol.
    `~base.abc.Real`
        Abstract base class corresponding to `~base.Real`.
    """

    def __eq__(self, other):
        return super().__eq__(other)

    def __ne__(self, other):
        return super().__ne__(other)

    def __lt__(self, other):
        return super().__lt__(other)

    def __le__(self, other):
        return super().__le__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __ge__(self, other):
        return super().__ge__(other)

    def __abs__(self):
        return super().__abs__()

    def __pos__(self):
        return super().__pos__()

    def __neg__(self):
        return super().__neg__()

    def __add__(self, other):
        return super().__add__(other)

    def __radd__(self, other):
        return super().__radd__(other)

    def __sub__(self, other):
        return super().__sub__(other)

    def __rsub__(self, other):
        return super().__rsub__(other)

    def __mul__(self, other):
        return super().__mul__(other)

    def __rmul__(self, other):
        return super().__rmul__(other)

    def __truediv__(self, other):
        return super().__truediv__(other)

    def __rtruediv__(self, other):
        return super().__rtruediv__(other)

    def __floordiv__(self, other):
        return super().__floordiv__(other)

    def __rfloordiv__(self, other):
        return super().__rfloordiv__(other)

    def __mod__(self, other):
        return super().__mod__(other)

    def __rmod__(self, other):
        return super().__rmod__(other)

    def __pow__(self, other):
        return super().__pow__(other)

    def __rpow__(self, other):
        return super().__rpow__(other)

