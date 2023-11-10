"""
Utility functions for checking data the property of numeric objects.
"""

import functools
import numbers
import typing

import numpy
import numpy.typing

from .. import container
from ._objects import Object


def isintegral(x):
    """True if is an object of integral type.

    This function exists to provide a single instance check against all integral
    types relevant to this package.
    """
    return isinstance(x, (numbers.Integral, numpy.integer))


def isclose(a: Object, b: numbers.Real) -> bool:
    """True if `b` is close to a value in `a`'s numeric data.
    
    This function is similar to (and, if fact, uses) `numpy.isclose`. The
    primary distinctions are that this function compares a single value to the
    real-valued data of a variable object and returns a single boolean value.
    
    Parameters
    ----------
    a : `~Object`
        The object that may contain `b`.

    b : real number
        The value for which to search.

    Notes
    -----
    - This function exists to handle cases in which floating-point arithmetic
      has caused a numeric operation to return an imprecise result, especially
      for small numbers (e.g., certain unit conversions). It will first test for
      standard containment via `in` before attempting to determine if `b` is
      close enough, within a very strict tolerance, to any member of `a`.
    """
    data = a.data
    if not container.isiterable(data):
        return a == b or numpy.isclose(b, data, atol=0.0)
    if b in data:
        return True
    if b < numpy.min(data) or b > numpy.max(data):
        return False
    return numpy.any([numpy.isclose(b, data, atol=0.0)])


def isequal(a, b):
    """True if `a` and `b` have equal numeric data.
    
    This is a convenience function that allows the caller to test whether two
    objects are numerically equivalent, even if they aren't strictly equal
    (perhaps because they have unequal metadata). If neither `a` nor `b` is an
    instance of `~Object`, calling this function is identical to calling
    `numpy.array_equal(a, b)`.
    """
    x = a.data if isinstance(a, Object) else a
    y = b.data if isinstance(b, Object) else b
    return numpy.array_equal(x, y)


@typing.overload
def hasdtype(
    a: typing.Union[Object, numpy.typing.ArrayLike],
    t: numpy.typing.DTypeLike,
    /,
): ...

@typing.overload
def hasdtype(
    a: typing.Union[Object, numpy.typing.ArrayLike],
    t: typing.Tuple[numpy.typing.DTypeLike],
    /,
): ...

def hasdtype(a, t, /):
    """True if `a` has one of the given data types.
    
    This function wraps `numpy.issubdtype` to allow the caller to pass more than
    one data type at a time, similar to the behavior of the built-in functions
    `isinstance` and `issubclass`.

    Parameters
    ----------
    a : `~Object` or array-like
        The object to check.
    t : dtype-like or tuple of dtype-like
        One or more objects that can be interpreted as `numpy` data types.

    Notes
    -----
    - If `a` is a `~Object`, this function will operate on `a.data`.
    - If the array-like operand (either `a` or `a.data`, as appropriate) is not
      a `numpy.ndarray`, this function will first convert it to one.
    """
    x = a.data if isinstance(a, Object) else a
    y = x if isinstance(x, numpy.ndarray) else numpy.array(x)
    dtype = y.dtype
    if isinstance(t, tuple):
        return any(numpy.issubdtype(dtype, i) for i in t)
    return numpy.issubdtype(dtype, t)


def implements(protocol, /):
    """Require that the data argument to a function implement `protocol`."""
    def wrapper(f):
        @functools.wraps(f)
        def check(self, data, *args, **kwargs):
            if isinstance(data, protocol):
                return f(self, data, *args, **kwargs)
            raise TypeError(
                f"Cannot instantiate class {type(self)}"
                f" with data that does not implement {protocol}"
            ) from None
        return check
    return wrapper


