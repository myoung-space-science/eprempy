"""
Partial implementations of certain abstract protocols, built on the
corresponding abstract base class.
"""

import typing

from . import _abcs
from . import _protocols


class Comparable(_abcs.Comparable):
    """Partial implementation of the comparable protocol.
    
    This mixin class provides concrete definitions of the following methods,
    based on concrete definitions of `__eq__` (called for `a == b`) and `__lt__`
    (called for `a < b`)

    - `__ne__`: not `a == b`
    - `__le__`: `a < b` or `a == b`
    - `__gt__`: not `a < b` and not `a == b`
    - `__ge__`: not `a < b`

    See Also
    --------
    `~quantity.Comparable`
        The corresponding abstract protocol class.
    `~quantity.abc.Comparable`
        The corresponding abstract base class.
    """

    def __ne__(self: _protocols.Comparable, other):
        return not (self == other)

    def __le__(self: _protocols.Comparable, other):
        return (self < other) or (self == other)

    def __gt__(self: _protocols.Comparable, other):
        return not (self < other) and not (self == other)

    def __ge__(self: _protocols.Comparable, other):
        return not (self < other)


class Complex(_abcs.Complex):
    """Partial implementation of the complex-valued protocol.
    
    This mixin class provides concrete definitions of the following methods,
    both based on concrete definitions of `__add__` (called for `a + b`) and
    `__neg__` (called for `-a`)

    - `__sub__`:  `a + (-b)`
    - `__rsub__`: `b + (-a)`

    See Also
    --------
    `~quantity.Complex`
        The corresponding abstract protocol class.
    `~quantity.abc.Complex`
        The corresponding abstract base class.
    """

    def __sub__(self: _protocols.Complex, other):
        if isinstance(other, _protocols.Complex):
            return self + (-other)
        return NotImplemented

    def __rsub__(self: _protocols.Complex, other):
        if isinstance(other, _protocols.Complex):
            return other + (-self)
        return NotImplemented


class Scalar(_abcs.Scalar):
    """Partial implementation of the scalar protocol.
    
    This mixin class provides a concrete definition of `__complex__`, based on a
    concrete definition of `__float__`.

    See Also
    --------
    `~quantity.Scalar`
        The corresponding abstract protocol class.
    `~quantity.abc.Scalar`
        The corresponding abstract base class.
    """

    def __complex__(self: _protocols.Scalar) -> complex:
        return complex(float(self))


class Sequence(_abcs.Sequence):
    """Partial implementation of the sequence-like protocol.
    
    This mixin class provides concrete definitions of the following methods,
    based on concrete definitions of `__getitem__` and `__iter__`. Both
    definitions mimic the respective definitions on `collections.abc.Sequence`.

    - `__contains__`
    - `__iter__`

    See Also
    --------
    `~quantity.Sequence`
        The corresponding abstract protocol class.
    `~quantity.abc.Sequence`
        The corresponding abstract base class.
    """

    def __contains__(self: _protocols.Sequence, v, /) -> bool:
        """Called for v in self."""
        for i in self:
            if i is v or v == i:
                return True
        return False

    def __iter__(self: _protocols.Sequence) -> typing.Iterator:
        """Called for iter(self)."""
        i = 0
        try:
            while True:
                v = self[i]
                yield v
                i += 1
        except IndexError:
            return

