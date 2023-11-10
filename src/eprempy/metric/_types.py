import abc
import typing

from ._units import Unit


T = typing.TypeVar('T')


class Interface(typing.Protocol[T]):
    """Abstract protocol class for metric objects.

    Objects that define the following properties are compatible with this
    protocol

    - `isunitless`, which should return a `bool`
    - `unit`, which should return a `~metric.Unit`
    """

    @property
    @abc.abstractmethod
    def isunitless(self: T) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def unit(self: T) -> Unit:
        raise NotImplementedError


@typing.runtime_checkable
class Type(typing.Protocol[T]):
    """Structural protocol class for metric objects.

    Objects that define the following properties will pass instance checks
    against this protocol

    - `isunitless`, which should return a `bool`
    - `unit`, which should return a `~metric.Unit`
    """

    @property
    def isunitless(self: T) -> bool: ...

    @property
    def unit(self: T) -> Unit: ...



