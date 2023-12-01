"""
Custom exception classes and support for working with general exceptions.

In addition to defining utilities designed to help with handling or checking
exceptions, this module defines all package-specific exception classes, in order
to make them more accessible to users and tests.
"""

import functools
import typing

# NOTE: This module should not import any modules from this package.


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


# ==== Custom exceptions that inherit from built-in exceptions ====

class ArgumentError(Exception):
    """Unknown or invalid argument."""


class AxisTypeError(TypeError):
    """Error in axis argument type."""


class AxisValueError(ValueError):
    """Error in axis argument value."""


class CLIError(Exception):
    """Invalid data generated by the CLI."""


class DimensionTypeError(Exception):
    """Invalid type for operation on dimensions."""


class InjectiveTypeError(TypeError):
    """The given mapping contains repeated values."""


class LogKeyError(KeyError):
    """The log has no entry for a given key."""


class MassValueError(Exception):
    """The given mass does not correspond to a known element."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"Cannot find an element with atomic mass {self.value}"


class MeasurableTypeError(TypeError):
    """Attempt to parse an unmeasurable type."""


class MeasurableValueError(ValueError):
    """Attempt to parse a measurable object with invalid value."""


class MeasurementTypeError(TypeError):
    """An object's `__measure__` method did not return a `~Measurement`."""


class MeasuringTypeError(TypeError):
    """An argument to `~measure` has an invalid type."""


class MergeError(Exception):
    """An error occurred while merging iterable objects."""


class NDimError(Exception):
    """Error related to array dimension."""


class NonExistentPathError(Exception):
    """A particular path does not exist."""

    def __init__(self, path: str=None):
        self._path = path

    @property
    def path(self) -> str:
        if self._path is None:
            self._path = "The requested path"
        return self._path

    def __str__(self):
        return f"{self.path} does not exist."


class NonInvertibleError(TypeError):
    """The given mapping is not invertible."""


class ObservationError(Exception):
    """There is an error in the observed array."""


class OperandTypeError(TypeError):
    """Wrong operand type for a numeric operation."""


class ParsingError(Exception):
    """Base class for exceptions encountered during symbolic parsing."""

    def __init__(self, arg: typing.Any) -> None:
        self.arg = arg


class PathTypeError(Exception):
    """The path is the wrong type."""


class PathOperationError(Exception):
    """This operation is not allowed on the given path(s)."""


class ProjectExistsError(Exception):
    """A project with this name already exists."""


class QuantityError(Exception):
    """An error occurred in `~metric.Quantity`."""


class ReadTypeError(Exception):
    """There is no support for reading the given file type."""


class SentinelInitError(Exception):
    """Attempt to directly instantiate a new sentinel object."""


class SentinelValueError(ValueError):
    """Value error while creating a sentinel object."""


class SymbolicTypeError(TypeError):
    """Type error associated with a symbolic expression."""


class SymbolicValueError(ValueError):
    """Value error associated with a symbolic expression."""


class SystemAmbiguityError(Exception):
    """The metric system is ambiguous."""


class TableKeyError(Exception):
    """No common key with this name."""

    def __str__(self) -> str:
        if len(self.args) > 0:
            return f"Table has no common key '{self.args[0]}'"
        return "Key not found in table"


class TableRequestError(Exception):
    """An exception occurred during standard look-up."""

    def __init__(self, request: typing.Mapping) -> None:
        self.request = request


class TableValueError(Exception):
    """An exception occurred during value-based look-up."""

    def __init__(self, value: typing.Any) -> None:
        self.value = value


class UnitParsingError(Exception):
    """Error when attempting to parse string into unit."""

    def __init__(self, string: str) -> None:
        self.string = string

    def __str__(self) -> str:
        return f"Could not determine unit and magnitude of '{self.string}'"


class UnitConversionError(Exception):
    """Unknown unit conversion."""


class UnitSystemError(Exception):
    """The metric system does not contain this unit."""


class UserError(Exception):
    """Incorrect use of a function (probably from the CLI)."""


# ==== Custom exceptions that inherit from other custom exceptions ====

class AmbiguousValueError(TableValueError):
    """Failed to find a unique entry by value."""

    def __str__(self) -> str:
        return f"No unique entry containing {self.value!r}"


class MissingValueError(TableValueError):
    """Failed to find any qualifying entries by value."""

    def __str__(self) -> str:
        return f"No entries containing {self.value!r}"


class AmbiguousRequestError(TableRequestError):
    """There are multiple instances of the same value for this key."""

    def __str__(self) -> str:
        """Print the requested pairs in the order provided."""
        items = list(self.request.items())
        n_items = len(items)
        if n_items <= 2:
            requested = " and ".join(f"'{k}={v}'" for k, v in items)
        else:
            these = ", ".join(f"'{k}={v}'" for k, v in items[:-1])
            this = f"'{items[-1][0]}={items[-1][1]}'"
            requested = f"{these}, and {this}"
        if n_items == 1:
            return f"The search criterion {requested} is ambiguous"
        return f"The search criteria {requested} are ambiguous"


class TableLookupError(TableRequestError):
    """Could not find the requested key-value pair(s)."""

    def __str__(self) -> str:
        """Print the requested pairs in the order provided."""
        items = list(self.request.items())
        if len(items) <= 2:
            criteria = " and ".join(f"{k}={v}" for k, v in items)
        else:
            these = ", ".join(f"{k}={v}" for k, v in items[:-1])
            this = f"{items[-1][0]}={items[-1][1]}"
            criteria = f"{these}, and {this}"
        return f"Table has no entry with {criteria}"


class ProductError(ParsingError):
    """The string contains a '*' after a '/'."""

    def __str__(self) -> str:
        return (
            f"The expression '{self.arg}' contains an ambiguous '*'."
            f" Please group '*' in parentheses when following '/'."
        )


class RatioError(ParsingError):
    """The string contains multiple '/' on a single level."""

    def __str__(self) -> str:
        return (
            f"The expression '{self.arg}' contains ambiguous '/'."
            f" Please refer to the NIST guidelines"
            f" (https://physics.nist.gov/cuu/Units/checklist.html)"
            f" for more information."
        )


