"""
Abstract protocols and base classes for general nunmeric quantities.
"""

from . import abc
from . import mixins
from ._protocols import (
    Additive,
    Algebraic,
    Array,
    Comparable,
    Complex,
    HasData,
    HasUnit,
    Multiplicative,
    Measurable,
    Measurement,
    Ordered,
    Real,
    Scalar,
    Sequence,
    Variable,
)
from ._types import (
    ArrayType,
    ComplexType,
    MeasurableType,
    MeasuredType,
    MeasurementType,
    MetricType,
    RealType,
    ScalarType,
    SequenceType,
)


__all__ = [
    # modules
    'abc',
    'mixins',
    # protocol classes
    'Additive',
    'Algebraic',
    'Array',
    'Comparable',
    'Complex',
    'HasData',
    'HasUnit',
    'Multiplicative',
    'Measurable',
    'Measurement',
    'Ordered',
    'Real',
    'Scalar',
    'Sequence',
    'Variable',
    # type variables
    'ArrayType',
    'ComplexType',
    'MeasurableType',
    'MeasuredType',
    'MeasurementType',
    'MetricType',
    'RealType',
    'ScalarType',
    'SequenceType',
]


def isordered(this, /):
    """True if `this` is an ordered object."""
    return isinstance(this, _protocols.Ordered)


def iscomparable(this, /):
    """True if `this` is a comparable object."""
    return isinstance(this, _protocols.Comparable)


def isadditive(this, /):
    """True if `this` is an additive object."""
    return isinstance(this, _protocols.Additive)


def ismultiplicative(this, /):
    """True if `this` is a multiplicative object."""
    return isinstance(this, _protocols.Multiplicative)


def isalgebraic(this, /):
    """True if `this` is an algebraic object."""
    return isinstance(this, _protocols.Algebraic)


def iscomplex(this, /):
    """True if `this` is a complex-valued object."""
    return isinstance(this, _protocols.Complex)


def isreal(this, /):
    """True if `this` is a real-valued object."""
    return isinstance(this, _protocols.Real)


def issequence(this, /):
    """True if `this` is an sequence-like object."""
    return isinstance(this, _protocols.Sequence)


def isarray(this, /):
    """True if `this` is an array-like object."""
    return isinstance(this, _protocols.Array)


def isscalar(this, /):
    """True if `this` is a scalar object."""
    return isinstance(this, _protocols.Scalar)


def isvariable(this, /):
    """True if `this` is a variable object."""
    return isinstance(this, _protocols.Variable)


def hasdata(this, /):
    """True if `this` has a `data` property."""
    return isinstance(this, _protocols.HasData)


def hasunit(this, /):
    """True if `this` has a `unit` property."""
    return isinstance(this, _protocols.HasUnit)


def ismeasured(this, /):
    """True if `this` is a measured object."""
    return isinstance(this, _protocols.Measured)


def ismeasurement(this, /):
    """True if `this` is a measurement-like object."""
    return isinstance(this, _protocols.Measurement)


def ismeasurable(this, /):
    """True if `this` is an explicitly measurable object."""
    return isinstance(this, _protocols.Measurable)



