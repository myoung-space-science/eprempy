import abc
import typing

from .. import base
from .. import numeric
from .. import metric


T = typing.TypeVar('T')


class Interface(numeric.Interface, typing.Protocol[T]):
    """Abstract protocol class for measured objects.

    A measured object has real-valued data and an associated metric unit.

    Objects that implement the numeric and metric protocols, and that define the
    following method, are compatible with this protocol

    - `to`, which should return a new instance of the implementing class
    """

    @property
    @abc.abstractmethod
    def isunitless(self: T) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def unit(self: T) -> metric.Unit:
        raise NotImplementedError

    @abc.abstractmethod
    def withunit(self: T, arg: metric.UnitLike) -> T:
        raise NotImplementedError


class Object(numeric.Object[base.RealType], Interface):
    """Abstract base class for measured objects.

    A measured object has real-valued data and an associated metric unit.

    This class adds an internal `_unit` attribute to `~numeric.Object`. It
    defines `isunitless` and `unit` properties. Concrete subclasses must
    implement the abstract method `to` from `~measured.Interface`.
    """

    @numeric.data.implements(base.Real)
    def __init__(
        self,
        data: base.RealType,
        unit: metric.Unit,
        /,
    ) -> None:
        super().__init__(data)
        self._unit = unit

    def __str__(self) -> str:
        return f"{self.data}, unit={str(self.unit)!r}"

    def __eq__(self, other) -> bool:
        if isinstance(other, Object):
            return (
                numeric.data.isequal(self.data, other.data)
                and
                self.unit == other.unit
            )
        return False

    @property
    def isunitless(self) -> bool:
        """True if this object's unit is '1'."""
        return self.unit == '1'

    @property
    def unit(self):
        """The metric unit of this object's data."""
        return self._unit


@typing.runtime_checkable
class Type(Interface[T], typing.Protocol):
    """Structural protocol class for measured objects.

    A measured object has real-valued data and an associated metric unit.

    In addition to attributes defined on `~data.Type`, calling code can expect
    the following attributes on an object that passes `isinstance(...,
    measured.Type)`

    - `unit` (property)
    - `isunitless` (property)
    - `to` (method)
    """

    _unit: metric.Unit

    @property
    def isunitless(self: T) -> bool: ...

    @property
    def unit(self: T) -> metric.Unit: ...

    def withunit(self: T, arg: metric.UnitLike) -> T: ...


