import typing

from .. import base
from .. import metric
from .. import measured
from .. import real
from ._functions import (
    isindexlike,
    ismeasurable,
    parse,
    hasdata,
    getdata,
)
from ._exceptions import (
    MeasuringTypeError,
    ParsingTypeError,
    ParsingValueError,
)
from ._measurement import Measurement


__all__ = [
    'isindexlike',
    'ismeasurable',
    'measure',
    'parse',
    'hasdata',
    'getdata',
    'MeasuringTypeError',
    'ParsingTypeError',
    'ParsingValueError',
    'Measurement',
]


@typing.overload
def measure(*args) -> Measurement:
    """Measure the given arguments, if possible.

    Parameters
    ----------
    *args
        One or more objects from which to create a measurement. See
        `~ismeasurable` for a description of supported object types.

    Returns
    -------
    `~Measurement`

    Raises
    ------
    `~MeasuringTypeError`
        The input was empty or the parsing algorithm was not able to determine
        appropriate numeric values and a unique unit from the input arguments.

    See Also
    --------
    `~measurable.parse`
        The function that parses measurable input into numeric values and an
        associated unit, if possible.
    `~measurable.ismeasurable`
        The function that detects measurable input.
    """

@typing.overload
def measure(x: measured.Object) -> Measurement:
    """Measure an existing measured object.
    
    Parameters
    ----------
    x : `~measured.Object`
        The measured object to measure. See Notes for additional information
        about how this function handles specific types of measured objects.

    Returns
    -------
    `~Measurement`

    Raises
    ------
    `~MeasurementTypeError`
        The type of object returned by `x.__measure__` was not an instance of
        `~Measurement`.

    Notes
    -----
    - If `x` is already an instance of `~Measurement`, this function will
      immediately return it.
    - If `x` implements the special method `__measure__`, this function will
      defer to that implementation.
    - If `x` is any other instance of `~measured.Object` or one of its
      subclasses, this function will create a new measurement from the
      real-valued data in `x.data` and the metric unit in `x.unit`.
    """


@typing.overload
def measure(x: base.MeasurableType, **kwargs) -> Measurement:
    """Measure an explicitly measurable object.
    
    Parameters
    ----------
    x
        An object that complies with the `~quantity.Measurable` protocol by
        implementing the special method `__measure__`.

    **kwargs
        Keyword arguments to pass to `x.__measure__`.

    Returns
    -------
    `~Measurement`

    Raises
    ------
    `~MeasurementTypeError`
        The type of object returned by `x.__measure__` was not an instance of
        `~Measurement`.
    """

def measure(*args, **kwargs):
    if not args:
        raise MeasuringTypeError("There is nothing to measure") from None
    this = args[0]
    if isinstance(this, Measurement):
        return this
    if isinstance(this, base.Measurable):
        return _measure_explicit(this, **kwargs)
    if isinstance(this, measured.Object):
        return measurement(this.data, unit=this.unit)
    return _measure_implicit(args)


def _measure_explicit(x: base.Measurable, **kwargs):
    """Create a measurement by calling `x.__measure__`."""
    result = x.__measure__(**kwargs)
    if not isinstance(result, (Measurement, base.Measurement)):
        raise MeasuringTypeError(
            f"{type(x)}.__measure__ returned"
            f" non-{Measurement} (type {type(result)})"
        )
    return result


def _measure_implicit(x):
    """Create a measurement by calling `metric.parse`."""
    try:
        parsed = parse(x, distribute=False)
    except (ParsingValueError, ParsingTypeError) as err:
        raise MeasuringTypeError(f"Cannot measure {x}") from err
    data = parsed[:-1]
    unit = parsed[-1]
    return measurement(data, unit=unit)


@typing.overload
def measurement(
    x: typing.Union[real.ValueType, typing.Sequence[real.ValueType]],
    /,
    unit: metric.Unit=typing.Literal['1']
) -> Measurement[real.ValueType]:
    """Create a physical measurement.
    
    Parameters
    ----------
    data : real number or sequence of real numbers
        The numerical value(s) from which to create a new measurement.

    unit : `~metric.Unit`
        The metric unit associated with `data`.

    Returns
    -------
    `~Measurement`

    Raises
    ------
    `TypeError`
        The caller passed a single non-numeric object or a sequence that
        includes non-numeric members.
    """

def measurement(*args, **kwargs):
    return _measurement.measurement_factory(*args, **kwargs)


