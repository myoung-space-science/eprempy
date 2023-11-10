"""
Utilities for defining factories of measured objects.
"""

import functools
import inspect
import typing

from ._objects import (
    Object,
    ObjectT,
)


def strict(*args):
    """Decorator function for enforcing attribute immutability.

    This function will raise a `ValueError` if it detects an attempt change the
    unit when creating a measured object from an existing measured object via
    the decorated factory function.
    """
    if all(isinstance(arg, str) for arg in args):
        func, keys = None, args
    elif len(args) == 1:
        arg = args[0]
        if callable(arg):
            func, keys = arg, ()
    else:
        raise TypeError(args)
    def decorate(__callable: typing.Callable[..., ObjectT]):
        return _check_metadata(__callable, *keys)
    if func is None:
        return decorate
    return decorate(func)


def returns(__type: typing.Type[ObjectT], strict: bool=True):
    """Mark the decorated object as the factory for the given type.

    Parameters
    ----------
    __type : subclass of `~Object`
        The type of object that the decorated function creates.

    strict : bool, default=True
        By default, this function will require that a given factory does not
        support changing the unit when creating a measured object from an
        existing measured object. Setting `strict=False` removes this
        restriction.

    See Also
    --------
    `~Object.factory`
        A class-method decorator that provides similar functionality.
    """
    def decorated(__callable: typing.Callable[..., ObjectT]):
        if issubclass(__type, Object):
            if strict:
                return __type.register.factory(_check_metadata(__callable))
            return __type.register.factory(__callable)
        raise TypeError(
            f"Cannot use {__callable} as the factory for {__type}"
            f", which is not a subtype of {Object}"
        ) from None
    return decorated


def _check_metadata(f: typing.Callable[..., ObjectT], *keys: str):
    """Internal logic for enforcing metadata immutability in factories."""
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
            if not keys:
                for k, v in kwargs.items():
                    if v is not None:
                        raise ValueError(errmsg.format(k)) from None
            for key in keys:
                if kwargs.get(key) is not None:
                    raise ValueError(errmsg.format(key)) from None
        return f(x, **kwargs)
    return wrapped


