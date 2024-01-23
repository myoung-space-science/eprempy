"""
Utilities for `eprem` tests.
"""
import numbers
import typing

import numpy
import numpy.typing

from eprempy import measured
from eprempy import metric
from eprempy import quantity


class Measurable:
    """An explicitly measurable object for tests.
    
    This class implements the special `__measure__` method declared in the
    `~quantity.Measurable` protocol and called by `~physical.measure`. It
    maintains internal attributes for numeric data and a metric unit, but does
    not define any public properties.
    """

    def __init__(self, x, /, unit=None) -> None:
        self._x = x
        self._unit = metric.unit(unit or '1')

    def __measure__(self) -> quantity.Measurement:
        return quantity.measurement(self._x, unit=self._unit)


class NDArrays(typing.NamedTuple):
    """The container of base `numpy` arrays."""
    r: numpy.typing.NDArray
    """The reference data."""
    xy: numpy.typing.NDArray
    """Data with the same dimensions as `original`."""
    yz: numpy.typing.NDArray
    """Data that shares one dimension with `original`."""
    zw: numpy.typing.NDArray
    """Data that shares no dimensions with `original`."""
    xyz: numpy.typing.NDArray
    """Data that has one more dimension than all others."""


def operation(
    f: typing.Callable,
    a: typing.Union[numpy.typing.ArrayLike, numbers.Real],
    b: typing.Union[numpy.typing.ArrayLike, numbers.Real],
    dimensions: typing.Iterable[typing.Iterable[str]]=None,
) -> numpy.typing.NDArray:
    """Compute `f(a, b)` consistent with `dimensions`.

    Parameters
    ----------
    f : callable
        An operator that accepts arguments of the types of elements in `a` and
        `b` and returns a single value of any type.

    a : array-like or real
        An array-like object with shape (I, J) or a real number.

    b : array-like or real
        An array-like object with shape (P, Q) or a real number.

    dimensions : iterable of iterables of strings, optional
        An two-element iterable containing the dimensions of `a` followed by the
        dimensions of `b`. The unique dimensions determine how this function
        reduces arrays `a` and `b`. This function will simply ignore
        `dimensions` if `a` or `b` is a number.

    Returns
    -------
    list
        A possibly nested list containing the element-wise result of `f`. The
        shape of the equivalent array will be consistent with the unique
        elements of `dimensions`.

    Notes
    -----
    This was created to help generalize tests of binary arithmetic operators on
    array-like objects. The way in which it builds arrays is not especially
    Pythonic; instead, the goal is to indicate how the structure of the
    resultant array arises from the structure of the operands.
    """
    x = float(a) if isinstance(a, numbers.Real) else numpy.array(a)
    y = float(b) if isinstance(b, numbers.Real) else numpy.array(b)
    return numpy.array(_compute(f, x, y, dimensions=dimensions))


def _compute(
    f: typing.Callable,
    a: typing.Union[numpy.typing.NDArray, float],
    b: typing.Union[numpy.typing.NDArray, float],
    dimensions: typing.Iterable[typing.Iterable[str]]=None,
) -> list:
    """Computation logic for `~support.operation`."""
    if isinstance(a, float) and isinstance(b, float):
        raise TypeError("Expected one of a or b to be an array")
    if not isinstance(a, float):
        I = range(len(a))
        J = range(len(a[0]))
    if not isinstance(b, float):
        P = range(len(b))
        Q = range(len(b[0]))
    if isinstance(b, float):
        return [
            # I x J
            [
                f(a[i][j], b) for j in J
            ] for i in I
        ]
    if isinstance(a, float):
        return [
            # P x Q
            [
                f(a, b[p][q]) for q in Q
            ] for p in P
        ]
    a_dims, b_dims = dimensions
    if a_dims[0] == b_dims[0] and a_dims[1] == b_dims[1]:
        # {x, y} * {x, y} -> {x, y}
        return [
            # I x J
            [
                # J
                f(a[i][j], b[i][j]) for j in J
            ] for i in I
        ]
    if a_dims[0] == b_dims[0]:
        # {x, y} * {x, z} -> {x, y, z}
        return [
            # I x J x Q
            [
                # J x Q
                [
                    # Q
                    f(a[i][j], b[i][q]) for q in Q
                ] for j in J
            ] for i in I
        ]
    if a_dims[1] == b_dims[0]:
        # {x, y} * {y, z} -> {x, y, z}
        return [
            # I x J x Q
            [
                # J x Q
                [
                    # Q
                    f(a[i][j], b[j][q]) for q in Q
                ] for j in J
            ] for i in I
        ]
    if a_dims[0] == b_dims[1]:
        # {y, z} * {x, y} -> {x, y, z}
        return [
            # P x I x J
            [
                # I x J
                [
                    # J
                    f(a[i][j], b[p][i]) for j in J
                ] for i in I
            ] for p in P
        ]
    # {x, y} * {z, w} -> {x, y, z, w}
    return [
        # I x J x P x Q
        [
            # J x P x Q
            [
                # P x Q
                [
                    # Q
                    f(a[i][j], b[p][q]) for q in Q
                ] for p in P
            ] for j in J
        ] for i in I
    ]


def compute_unit(f, a, b):
    """Apply `f` to the operands' unit(s)."""
    if isinstance(a, measured.Object) and isinstance(b, measured.Object):
        return f(a.unit, b.unit)
    if isinstance(a, numbers.Real) and isinstance(b, measured.Object):
        return f('1', b.unit)
    if isinstance(a, measured.Object) and isinstance(b, numbers.Real):
        return a.unit
    if isinstance(a, tuple) and isinstance(b, measured.Object):
        return f(a[-1], b.unit)
    if isinstance(a, measured.Object) and isinstance(b, tuple):
        return f(a.unit, b[-1])
    raise TypeError(a, b)


