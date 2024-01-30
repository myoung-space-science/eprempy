import contextlib
import numbers
import typing
import typing_extensions

import numpy

from .. import base
from .. import container
from .. import etc
from .. import measured
from .. import metric
from .. import numeric
from .. import real
from ._exceptions import (
    ParsingTypeError,
    ParsingValueError,
)


def isindexlike(x, /):
    """True if the input can index an axis."""
    if isinstance(x, (numeric.index.Value, numeric.index.Sequence)):
        return True
    for f in (numeric.index.value, numeric.index.sequence):
        with contextlib.suppress(TypeError, ValueError):
            f(x)
            return True
    return False


def ismeasurable(x, /):
    """True if the user can expect to be able to measure the input.

    A measurable object may be:
    
    - an object that satisfies the `~quantity.Measurable` protocol
    - a real number
    - an iterable of real numbers
    - an iterable of real numbers followed by a unit-like object
    - an two-element iterable whose first element is an iterable of real numbers
      and whose second element is a unit-like object
    - an iterable of any of the previous objects.

    Parameters
    ----------
    x
        The candidate measurable object.

    Returns
    -------
    bool
        True if `x` is measurable; false otherwise.

    See Also
    --------
    `~measure`
        Create a `~Measurement` from measurable input.
    """
    args = container.unwrap(x)
    if etc.isnull(x):
        return False
    if base.ismeasurable(args):
        return True
    if isinstance(args, numbers.Real):
        return True
    if not container.isseparable(args):
        return False
    if all(isinstance(arg, numbers.Real) for arg in args):
        return True
    if metric.unitlike(args[-1]):
        arg0 = args[0]
        values = arg0 if container.isiterable(arg0) else args[:-1]
        if all(isinstance(value, numbers.Real) for value in values):
            return True
    if all(isinstance(i, (list, tuple)) and ismeasurable(i) for i in args):
        return True
    return False


Ns = typing_extensions.TypeVarTuple('Ns')

@typing.overload
def parse(
    x: real.ValueType,
    /,
) -> typing.Tuple[real.ValueType, typing.Literal['1']]: ...

@typing.overload
def parse(
    x: typing.Tuple[real.ValueType, str],
    /,
) -> typing.Tuple[real.ValueType, str]: ...

@typing.overload
def parse(
    x: typing.Tuple[real.ValueType, ...],
    /,
) -> typing.Tuple[typing_extensions.Unpack[Ns], typing.Literal['1']]: ...

@typing.overload
def parse(
    x: typing.Tuple[typing_extensions.Unpack[Ns], str],
    /,
) -> typing.Tuple[typing_extensions.Unpack[Ns], str]: ...

@typing.overload
def parse(
    x: typing.Tuple[typing_extensions.Unpack[Ns], str],
    /,
    distribute: typing.Literal[False],
) -> typing.Tuple[typing_extensions.Unpack[Ns], str]: ...

@typing.overload
def parse(
    x: typing.Tuple[typing_extensions.Unpack[Ns], str],
    /,
    distribute: typing.Literal[True],
) -> typing.Tuple[typing.Tuple[numbers.Real, str], ...]: ...

def parse(x, /, distribute: bool=False):
    """Parse an implicitly measurable object.
    
    This function will extract numeric values and an associated unit from `x`,
    if possible.

    Parameters
    ----------
    x
        The object or collection of objects to measure.

    distribute : bool, default=false
        If true, distribute the parsed unit among parsed numerical values.

    Returns
    -------
    `tuple`
        - If `distribute == True`, the returned tuple will contain one or more
          `tuple`s, each containing a single numeric value and a string that
          represents the associated unit common to all values. The length of the
          result will equal the number of parsed numeric values.
        - Otherwise, the returned `tuple` will contain parsed numeric values
          followed by a single unit string. The length of the result will be one
          more than the number of original numeric values.

    Raises
    ------
    `~ParsingTypeError`
        - The input is any non-iterable object but is not a single number.

    `~ParsingValueError`
        - The input is an empty iterable object.
        - The input contains multiple units.
        - The input contains multiple objects with individual units, but the
          units differ.

    Notes
    -----
    This function will parse the following types of arguments

    - a single number
    - a `list` or `tuple` of only numbers
    - a `list` or `tuple` of numbers followed by a single unit
    - a 2-element `list` or `tuple` in which the first element is a `list` or
      `tuple` of only numbers, and the second element is a single unit
    - an iterable collection of any of the above cases, as long as the units are
      consistent

    where the notion of numbers includes strings that can be converted to
    numeric values.
    """

    # Strip redundant lists and tuples.
    unwrapped = container.unwrap(x)

    # Raise a type-based exception if input is `None`.
    if unwrapped is None:
        raise ParsingTypeError(f"Cannot measure {unwrapped!r}") from None

    # Raise a value-based exception for empty input.
    if etc.isnull(unwrapped):
        raise ParsingValueError(
            f"Cannot measure empty input: {unwrapped!r}"
        ) from None

    # Handle a single numeric value.
    if isinstance(unwrapped, numbers.Real):
        result = (unwrapped, '1')
        return (result,) if distribute else result

    # Handle a single numerical string.
    if isinstance(unwrapped, str):
        try:
            result = (float(unwrapped), '1')
        except (ValueError, TypeError) as err:
            raise ParsingTypeError(
                f"Cannot measure non-numeric string {unwrapped!r}"
            ) from err
        return (result,) if distribute else result

    # Raise a type-based exception if input is not iterable.
    try:
        iter(unwrapped)
    except TypeError as err:
        raise ParsingTypeError(
            f"Cannot measure non-iterable input: {unwrapped!r}"
        ) from err

    # Recursively parse nested parsable objects.
    if all(isinstance(arg, (list, tuple)) for arg in unwrapped):
        return _recursive_parse(unwrapped, distribute)

    # Count the number of distinct unit-like objects.
    types = [type(arg) for arg in unwrapped]
    counted = {t: types.count(t) for t in (str, metric.Unit)}

    # Check for multiple units.
    errmsg = "You may only specify one unit."
    if counted[metric.Unit] > 1:
        # If the input contains more than one instance of the `Unit` class,
        # there is nothing we can do to salvage it.
        raise ParsingValueError(errmsg) from None
    if counted[str] > 1:
        # First, check for a single numeric string.
        if isinstance(unwrapped, str):
            with contextlib.suppress(ValueError):
                return parse([float(unwrapped)])
        # Next, check for all numeric strings.
        with contextlib.suppress(ValueError):
            return parse([float(arg) for arg in unwrapped])
        # Finally, check for numeric strings with a final unit.
        try:
            values = [float(arg) for arg in unwrapped[:-1]]
        except ValueError as err:
            raise ParsingValueError(errmsg) from err
        return parse([*values, unwrapped[-1]])

    # Handle flat numerical iterables, like (1.1,) or (1.1, 2.3).
    if all(isinstance(arg, numbers.Real) for arg in unwrapped):
        return _wrap_measurable(unwrapped, '1', distribute)

    # Ensure an explicit unit-like object. Note that, at this point, `unwrapped`
    # must have one of the following forms (where any tuple may be a list):
    # - (v0, v1, ..., unit)
    # - ((v0, v1, ...), unit)
    last = unwrapped[-1]
    unitless = all(
        not isinstance(arg, (str, metric.Unit)) for arg in unwrapped
    ) or last in ['1', metric.unit('1')]
    unit = '1' if unitless else str(last)

    if isinstance(last, (str, metric.Unit)):
        unit = str(unwrapped[-1])

        # Handle flat iterables with a unit, like (1.1, 'm') or (1.1, 2.3, 'm').
        if all(isinstance(arg, numbers.Real) for arg in unwrapped[:-1]):
            return _wrap_measurable(unwrapped[:-1], unit, distribute)

        # Handle iterable values with a unit, like [(1.1, 2.3), 'm'].
        if isinstance(unwrapped[0], (list, tuple, range)):
            return _wrap_measurable(unwrapped[0], unit, distribute)

    raise ParsingTypeError(x)


def _wrap_measurable(values, unit, distribute: bool):
    """Wrap a parsed measurable and return to caller."""
    if distribute:
        return tuple(container.distribute(values, unit))
    return (*values, unit)


def _recursive_parse(unwrapped, distribute: bool):
    """Parse the measurable by calling back to `~parse`."""
    if distribute:
        parsed = [
            item
            for arg in unwrapped
            for item in parse(arg, distribute=True)
        ]
        return tuple(parsed)
    parsed = [
        parse(arg, distribute=False) for arg in unwrapped
    ]
    units = [item[-1] for item in parsed]
    if any(unit != units[0] for unit in units):
        errmsg = "Cannot combine measurements with different units."
        raise ParsingValueError(errmsg)
    values = [
        i for item in parsed for i in item[:-1]
    ]
    unit = units[0]
    return (*values, unit)


def hasdata(a):
    """True if the argument appears to contain numeric data."""
    return getdata(a) is not None # NOTE: data could be 0


def getdata(a):
    """Get the argument's numeric data, if any."""
    if isinstance(a, measured.Object):
        return a.data
    if isinstance(a, (numbers.Number, numpy.number, numpy.ndarray)):
        return a
    with contextlib.suppress(ParsingTypeError, ParsingValueError):
        parsed = parse(a, distribute=False)
        data = parsed[:-1]
        if len(data) > 1:
            return numpy.array(data)
        return data[0]


