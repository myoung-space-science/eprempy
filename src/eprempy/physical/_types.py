import abc
import typing

from .. import base
from .. import measured
from .. import metric
from .. import numeric
from .. import quantity


class Quantity(measured.Object[base.RealType], base.abc.Real):
    """Abstract base class for all physical objects."""

QuantityType = typing.TypeVar('QuantityType', bound=Quantity)


T = typing.TypeVar('T')


class Protocol(measured.Interface, base.Real, typing.Protocol[T]):
    """Abstract protocol class for physical objects.
    
    A physical object is a real-valued measurable object. In addition to all
    abstract properties and methods inherited from from `~measured.Protocol`, a
    physical object must implement the real-valued protocol (defined by
    `~base.Real`) and must implement the `__measure__` method.
    """

    @abc.abstractmethod
    def __measure__(self) -> quantity.Measurement:
        """Called for `~quantity.measure(self)`."""
        raise NotImplementedError


@typing.runtime_checkable
class Type(Protocol, typing.Protocol[T]):
    """Structural protocol clas for physical objects."""

    def __measure__(self) -> quantity.Measurement: ...


@typing.runtime_checkable
class ArrayType(numeric.Type, metric.Type, typing.Protocol):
    """Structural protocol class for physical arrays.

    Objects that define the following properties will pass instance checks
    against this protocol

    - `data`
    - `unit`
    - `isunitless`
    - `dimensions`

    See Also
    --------
    `~numeric.Type`
        The protocol class that requires `data`.
    `~metric.Type`
        The protocol class that requires `unit` and `isunitless`.
    """

    @property
    def dimensions(self) -> numeric.Dimensions: ...


