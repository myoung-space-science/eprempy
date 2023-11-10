import functools
import typing


T = typing.TypeVar('T')
G = typing.TypeVar('G')


class Wrapper:
    """Substitute default values for exceptions.

    This class wraps a callable object in `try/except` logic that substitutes a
    default value when calling that object raises a known exception. The default
    behavior is to substitute `None`, but users may specify a specific
    substitution value when registering a known exception (see the `catch`
    method of this class).
    
    Examples
    --------
    Define a function that only inverts positive numbers:

    >>> def invert(v):
    ...     if v < 0:
    ...         raise ValueError
    ...     return 1 / v

    Create an instance of this class that wraps `invert`:

    >>> wrapper = exceptions.Wrapper(invert)

    Register `TypeError` with the default substitution, `None`, and register
    `ZeroDivisionError` with a custom substitution:
    
    >>> wrapper.catch(TypeError)
    >>> wrapper.catch(ZeroDivisionError, 'Bad!')

    A valid call to `invert` returns the expected result:

    >>> wrapper.call(2)
    0.5

    Passing a string argument raises a `TypeError` in `invert`, which `wrapper`
    converts to `None`:

    >>> wrapper.call('2')

    Triggering a `ZeroDivisionError` in `invert` causes `wrapper` to return the
    registered substitution:

    >>> wrapper.call(0)
    'Bad!'

    Passing a negative raises a `ValueError` in `invert`. Since we did not
    register this type of exception, it propagates back to us:

    >>> wrapper.call(-1)
    ...
    ValueError

    Notes
    -----
    This class was inspired by https://stackoverflow.com/a/8915613/4739101.
    """

    def __init__(self, __callable: typing.Callable[..., T]) -> None:
        self._f = __callable
        self._substitutions = {}

    def catch(self, exception: Exception, /, value: G=None):
        """Register a known exception and optional substitution value.
        
        Parameters
        ----------
        exception
            An exception class to catch when calling the wrapped object.

        value, optional
            The value to return from `call` when calling the wrapped object
            raises `exception`. The default value is `None`. There is one
            special case: Registering `exception` with `value = ...` (i.e., the
            built-in `Ellipsis` object), will cause `call` to return the given
            argument(s). See `call` for more information about the form of the
            return value in this case.
        """
        self._substitutions[exception] = value
        return self

    def compute(self, *args, **kwargs) -> typing.Union[T, G]:
        """Call the wrapped object with the given arguments.
        
        Parameters
        ----------
        *args
            Positional arguments to pass to the wrapped object.

        **kwargs
            Keyword arguments to pass to the wrapped object.

        Returns
        -------
        The result of calling the wrapped object, or an associated default
        value, or the given arguments.
        
        If no exceptions arose when calling the wrapped object, this method will
        return the result of that call.

        If calling the wrapped object raises a known exception and the value
        associated with that exception is not `...` (i.e., the built-in
        `Ellipsis` object), this method will return the associated value.
        
        If calling the wrapped object raises a known exception and the value
        associated with that exception is `...`, this method will return the
        given arguments. The return type in this case depends on the given
        arguments. If the user passes only a single positional argument, this
        method will return that argument. If the user passes only positional
        arguments, this method will return the equivalent `tuple`. If the user
        passes only keyword arguments, this method will return the equivalent
        `dict`. If the user passes positional and keyword arguments, this method
        will return a `tuple` containing the corresponding equivalent `tuple`
        and `dict`.
        
        If calling the wrapped object raises an exception that is unknown to
        this instance, that exception will propagate up to the caller as usual.
        """
        try:
            return self._f(*args, **kwargs)
        except tuple(self._substitutions) as err:
            value = self._substitutions[type(err)]
            if value != Ellipsis:
                return value
            if not kwargs:
                if len(args) == 1:
                    return args[0]
                return args
            if not args:
                return kwargs
            return args, kwargs


@typing.overload
def convert(expected, replacement, /):
    """Replace an expected exception."""

@typing.overload
def convert(expected: Exception, replacement: G, /) -> G:
    """Replace the expected exception with the given value.

    Parameters
    ----------
    expected : exception
        A subtype of `Exception` to catch.
    replacement
        The value to return after catching the expected exception.
    """

@typing.overload
def convert(
    expected: Exception,
    replacement: Exception,
    /,
    message: typing.Optional[str]=None,
) -> typing.NoReturn:
    """Replace the expected exception with a different exception.

    Parameters
    ----------
    expected : exception
        A subtype of `Exception` to catch.
    replacement : exception
        The exception to raise after catching the expected exception.
    message : string, optional
        The error message to include with the replacement exception.
    """

def convert(expected, replacement, /, message=None):
    def wrapper(f: typing.Callable[..., T]):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
            except expected as err:
                if isexception(replacement):
                    exc = replacement(message) if message else replacement
                    raise exc from err
                return replacement
            return result
        return wrapped
    return wrapper


def isexception(x):
    """True if `x` is a subtype of `Exception`."""
    try:
        truth = issubclass(x, Exception)
    except TypeError:
        return False
    return truth


