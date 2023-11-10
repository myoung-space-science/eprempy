"""
Operators on arbitrary numeric objects.

This module provides a canonical namespace for all relevant standard-library
numeric operators. It also defines the aliased mappings that appear as
`~numeric.OPERATIONS` and `~numeric.OPERATORS`, as well as a utility function,
`get`, for retrieving canonical operators by name or functional group.
"""

from builtins import (
    pow,
    round,
)
from math import (
    floor,
    ceil,
    trunc,
)
from operator import (
    eq,
    ne,
    lt,
    le,
    gt,
    ge,
    abs,
    pos,
    neg,
    add,
    sub,
    mul,
    truediv,
    floordiv,
    mod,
)
import typing


__all__ = [
    'eq',
    'ne',
    'lt',
    'le',
    'gt',
    'ge',
    'abs',
    'pos',
    'neg',
    'round',
    'floor',
    'ceil',
    'trunc',
    'add',
    'sub',
    'mul',
    'truediv',
    'floordiv',
    'mod',
    'pow',
]


def __int__(self):
    """Called for int(self)."""
    return int(self)


def __float__(self):
    """Called for float(self)."""
    return float(self)


def __complex__(self):
    """Called for complex(self)."""
    return complex(self)


def __eq__(self, other):
    """Called for self == other."""
    return eq(self, other)


def __ne__(self, other):
    """Called for self != other."""
    return ne(self, other)


def __lt__(self, other):
    """Called for self < other."""
    return lt(self, other)


def __gt__(self, other):
    """Called for self > other."""
    return gt(self, other)


def __le__(self, other):
    """Called for self <= other."""
    return le(self, other)


def __ge__(self, other):
    """Called for self >= other."""
    return ge(self, other)


def __abs__(self):
    """Called for abs(self)."""
    return abs(self)


def __pos__(self):
    """Called for +self."""
    return pos(self)


def __neg__(self):
    """Called for -self."""
    return neg(self)


def __round__(self, ndigits: typing.Optional[int]=None):
    """Called for round(self)."""
    return round(self, ndigits=ndigits)


def __floor__(self):
    """Called for math.floor(self)."""
    return floor(self)


def __ceil__(self):
    """Called for math.ceil(self)."""
    return ceil(self)


def __trunc__(self):
    """Called for math.trunc(self)."""
    return trunc(self)


def __add__(self, other):
    """Called for self + other."""
    return add(self, other)


def __radd__(self, other):
    """Called for other + self."""
    return add(other, self)


def __iadd__(self, other):
    """Called for self += other."""
    return add(self, other)


def __sub__(self, other):
    """Called for self - other."""
    return sub(self, other)


def __rsub__(self, other):
    """Called for other - self."""
    return sub(other, self)


def __isub__(self, other):
    """Called for self -= other."""
    return sub(self, other)


def __mul__(self, other):
    """Called for self * other."""
    return mul(self, other)


def __rmul__(self, other):
    """Called for other * self."""
    return mul(other, self)


def __imul__(self, other):
    """Called for self *= other."""
    return mul(self, other)


def __truediv__(self, other):
    """Called for self / other."""
    return truediv(self, other)


def __rtruediv__(self, other):
    """Called for other / self."""
    return truediv(other, self)


def __itruediv__(self, other):
    """Called for self /= other."""
    return truediv(self, other)


def __floordiv__(self, other):
    """Called for self // other."""
    return floordiv(self, other)


def __rfloordiv__(self, other):
    """Called for other // self."""
    return floordiv(other, self)


def __ifloordiv__(self, other):
    """Called for self //= other."""
    return floordiv(self, other)


def __mod__(self, other):
    """Called for self % other."""
    return mod(self, other)


def __rmod__(self, other):
    """Called for other % self."""
    return mod(other, self)


def __imod__(self, other):
    """Called for self %= other."""
    return mod(self, other)


def __pow__(self, other, mod: typing.Optional[int]=None):
    """Called for self ** other."""
    return pow(self, other, mod=mod)


def __rpow__(self, other, mod: typing.Optional[int]=None):
    """Called for other ** self."""
    return pow(other, self, mod=mod)


def __ipow__(self, other, mod: typing.Optional[int]=None):
    """Called for self **= other."""
    return pow(self, other, mod=mod)


