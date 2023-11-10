import typing

from ._operations import resolve


T = typing.TypeVar('T')


class Result:
    """Container class for the result of an operation."""

    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def apply(self, f: typing.Callable[..., T]) -> T:
        """Create a new object by applying `f` to this result."""
        return f(*self.args, **self.kwargs)

    @property
    def args(self):
        """The declared positional arguments of this result."""
        return self._args

    @property
    def kwargs(self):
        """The declared keyword arguments of this result."""
        return self._kwargs


@typing.runtime_checkable
class Customizable(typing.Protocol):
    """Structural protocol for objects that implement custom operators."""
    def __object_operator__(self, f, *args, **kwargs) -> typing.Any: ...


def unary(operation: typing.Union[str, typing.Callable]):
    """Implement a unary numeric operation."""
    f = resolve(operation)
    def operator(self, **kwargs):
        if isinstance(self, Customizable):
            return self.__object_operator__(f, self, **kwargs)
        return NotImplemented
    return operator


def binary(operation: typing.Union[str, typing.Callable]):
    """Implement a binary numeric operation."""
    f = resolve(operation)
    def operator(self, other, **kwargs):
        if isinstance(self, Customizable):
            return self.__object_operator__(f, self, other, **kwargs)
        return NotImplemented
    return operator


def doublet(operation: typing.Union[str, typing.Callable]):
    """Implement a forward/reverse pair of binary numeric operations."""
    f = resolve(operation)
    def forward(self, other, **kwargs):
        if isinstance(self, Customizable):
            return self.__object_operator__(f, self, other, **kwargs)
        return NotImplemented
    def reverse(self, other, **kwargs):
        if isinstance(self, Customizable):
            return self.__object_operator__(f, other, self, **kwargs)
        return NotImplemented
    return forward, reverse


