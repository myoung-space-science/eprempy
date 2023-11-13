"""
Base classes for objects that provide an interface to numeric data.
"""

import collections.abc
import functools
import inspect
import numbers
import typing

from .. import etc
from ..typehelp import Self


ValueType = typing.TypeVar('ValueType', int, float, complex, numbers.Complex)
"""Type variable representing a numeric value.

This type variable is constrained to be one of the following standard types

- `int`
- `float`
- `complex`
- `numbers.Complex`
"""

T = typing.TypeVar('T')

# NOTE: These are a WIP attempt to define a generic type variable that
# represents either a single number or an array-like object of arbitrary depth
# that contains only numbers. So far, it works for single numbers and nested
# lists, but not for `numpy` arrays.
_NestedSequence = typing.Union[
    typing.Sequence[T],
    typing.Sequence["_NestedSequence[T]"],
]
DataType = typing.Union[
    ValueType,
    _NestedSequence[ValueType],
]


class Registry(collections.abc.Mapping, typing.Generic[T]):
    """A collection of decorators for setting numeric-object attributes."""

    def __init__(self, __type: typing.Type[T]) -> None:
        self._type = __type
        self._registered = {'factory': __type}

    @typing.overload
    def factory(*, mutable: typing.Optional[typing.Sequence[str]]=None): ...

    def factory(
        self,
        f: typing.Callable[..., T]=None,
        *,
        mutable: typing.Optional[typing.Sequence[str]]=None,
    ) -> typing.Callable[..., T]:
        """Set the object factory.

        This method is intended for use as a decorator. When called as a
        standard decorator, it will prevent attempts to update attributes when
        the first argument is an existing instance of the class. When called
        with a sequence of attribute names, it will relax the immutability
        restriction on the named attributes.
        """
        keys = mutable or []
        def decorate(c: typing.Callable[..., T]):
            wrapped = _wrap_factory(c, *keys)
            self._registered['factory'] = wrapped
            return wrapped
        if f is None:
            return decorate
        return decorate(f)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self._registered)

    def __iter__(self) -> typing.Iterator:
        """Called for iter(self)."""
        return iter(self._registered)

    def __getitem__(self, __k: str):
        """Called for key-based access."""
        try:
            value = self._registered[__k]
        except KeyError as err:
            raise KeyError(
                f"This collection does not include {__k!r}"
            ) from err
        return value


class Registered(typing.Generic[T]):
    """Interface to registered attributes."""

    def __init__(self, registry: Registry[T]) -> None:
        self.registry = registry

    @property
    def factory(self) -> typing.Callable[..., T]:
        """The registered object factory, if any."""
        return self._getattr('factory')

    def _getattr(self, name: str):
        """Internal attribute look-up method."""
        try:
            this = self.registry[name]
        except KeyError as err:
            raise AttributeError(name) from err
        return this


class Mixin:
    """Class methods and properties for numeric objects."""

    register: typing.ClassVar[Registry[Self]]=None

    @classmethod
    def spawn(cls, x, **metadata):
        """Create a new instance of this type."""
        return cls._spawn(x, **metadata)

    @classmethod
    def _spawn(cls, *args, **kwargs):
        """Create a new instance of this type."""
        if cls.has('factory'):
            return cls.registered.factory(*args, **kwargs)
        raise NotImplementedError(
            f"{cls} does not have an associated instance factory"
        ) from None

    @classmethod
    def has(cls, name: str):
        """True if this class has registered the named attribute."""
        if cls.register is None:
            return False
        return cls.register.get(name) is not None

    @etc.classproperty
    def registered(cls):
        """The collection of registered attributes."""
        return Registered(cls.register)


class Quantity(Mixin, typing.Generic[T]):
    """Base class for generic interfaces."""

    def __init_subclass__(cls, **kwargs) -> None:
        """Defined to reset the attribute registry on each subclass."""
        super().__init_subclass__(**kwargs)
        cls.register = Registry(cls)

    def __init__(self, __object: T) -> None:
        self._object = __object

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}[{type(self._object)}]"


@etc.autostr
class Interface(typing.Protocol[T]):
    """Abstract protocol class for interfaces to numeric data.

    This class defines an internal `_data` attribute and a public `data`
    property, and provides basic `__str__` and `__repr__` methods.
    """

    _data: T

    @property
    def data(self) -> T:
        """This object's underlying data."""
        return self._data


InterfaceT = typing.TypeVar('InterfaceT', bound=Interface)
"""Type variable bounded by `~numeric.Interface`."""


class Object(Interface[T], Mixin):
    """A concrete interface to numeric data.

    This class inherits the internal `_data` attribute and the public `data`
    property from `~Interface`. It extends that class by providing a concrete
    initialization method, as well as basic string-representation methods.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        """Defined to reset the attribute registry on each subclass."""
        super().__init_subclass__(**kwargs)
        cls.register = Registry(cls)

    def __init__(self, data: T) -> None:
        """Initialize this object with `data`."""
        self._data = data

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return str(self.data)


ObjectT = typing.TypeVar('ObjectT', bound=Object)
"""Type variable bounded by `~numeric.Object`."""


@typing.runtime_checkable
class Type(typing.Protocol[T]):
    """Structural protocol class for generic data-centric objects.

    Objects that define a `_data` attribute and a `data` property will pass
    instance checks against this protocol.
    """

    _data: T

    @property
    def data(self) -> T: ...


def _wrap_factory(f: typing.Callable[..., ObjectT], *keys: str):
    """Internal logic for checking numeric-object factories."""
    rettype = inspect.signature(f).return_annotation
    newtype = Object if rettype is inspect.Signature.empty else rettype
    @functools.wraps(f)
    def wrapped(x, /, **kwargs):
        rtstr = newtype.__qualname__
        xtstr = type(x).__qualname__
        rest = (
            f"when creating an instance of {rtstr}"
            f" from an existing instance of {xtstr}"
        )
        errmsg = "Cannot change {} " + rest
        if isinstance(x, Object):
            for k, v in kwargs.items():
                if k not in keys and v is not None:
                    raise ValueError(errmsg.format(repr(k))) from None
        return f(x, **kwargs)
    return wrapped


