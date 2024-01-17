"""
Objects and utilities relevant to metric properties and systems.
"""

import typing

from ._conversions import (
    convert,
)
from ._defined import (
    UNITS,
    DIMENSIONS,
    NamedUnit,
    Reduction,
    identify,
    ratio,
)
from ._dimensions import (
    dimension_factory as dimension,
    Dimension,
)
from ._exceptions import (
    UnitConversionError,
    UnitParsingError,
)
from ._reference import (
    CONVERSIONS,
    SYSTEMS,
    standardize,
)
from ._systems import (
    system_factory as system,
    quantity_factory as quantity,
    Quantity,
    System,
)
from ._types import (
    Interface,
    Type,
)
from ._units import (
    normalize,
    unit_factory as unit,
    Unit,
    UnitLike,
    unitlike,
)

__all__ = [
    'CONVERSIONS',
    'DIMENSIONS',
    'SYSTEMS',
    'UNITS',
    'Conversion',
    'Dimension',
    'Interface',
    'NamedUnit',
    'Reduction',
    'Quantity',
    'System',
    'Type',
    'Unit',
    'UnitConversionError',
    'UnitLike',
    'UnitParsingError',
    'convert',
    'dimension',
    'identify',
    'normalize',
    'quantity',
    'ratio',
    'standardize',
    'system',
    'unit',
    'unitlike',
]


class Conversion(_conversions.Conversion):
    """The result of a unit conversion."""

    @property
    def old(self):
        """The original unit."""
        return unit(self.u0)

    @property
    def new(self):
        """The converted unit."""
        return unit(self.u1)


@typing.overload
def conversion(
    source: typing.Union[str, Unit],
    target: typing.Union[str, Unit],
    quantity: typing.Optional[str]=None,
) -> Conversion: ...

@typing.overload
def conversion(
    source: typing.Union[str, Unit],
    target: typing.Union[str, Unit],
    error: typing.Literal[False],
    quantity: typing.Optional[str]=None,
) -> typing.Optional[Conversion]: ...

def conversion(source, target, **kwargs):
    """Compute the conversion from `source` to `target`, if possible.

    Parameters
    ----------
    source : string or `~metric.Unit`
        The unit from which to convert.

    target : string or `~metric.Unit`
        The unit or metric system to which to convert.

    error : bool, default=True
        If false, return `None` for a failed conversion. The default behavior is
        to allow undefined conversions to raise `~metric.UnitConversionError`.

    quantity : string, optional
        The physical quantity associated with `source`.

    Returns
    -------
    `~Conversion` or `None`
        An object representing the conversion from `source` to `target`,
        including the relevant numerical factor, if the conversion was
        successful. The value of `error` determines the behavior if the
        conversion fails.

    Examples
    --------
    As a simple first example, suppose you have something that is 2 meters long
    and you want to convert its length to centimeters:

    >>> 2 * float(metric.conversion('m', 'cm'))
    200.0

    This simple case is equivalent to computing the metric ratio of meter to
    centimeter because they have the same base unit:

    >>> 2 * metric.ratio('m', 'cm')
    200.0

    As a more complex example, suppose you have an amount of energy flux in 'J /
    au^2'. In order to convert to the equivalent amount in 'eV / km^2', you must
    multiply by

    >>> float(metric.conversion('J / au^2', 'eV / km^2'))
    278.8896829059863

    which is the same as first multiplying by the factor to convert from 'J' to
    'eV', then dividing by the square of the factor to convert from 'au' to
    'km', as shown below

    >>> c0 = metric.conversion('J', 'eV')
    >>> c1 = metric.conversion('au', 'km')
    >>> float(c0)
    6.241418050181001e+18
    >>> float(c1)
    149597870.70000002
    >>> float(c0) / float(c1)**2
    278.8896829059863

    This function also supports converting the original unit to the equivalent
    unit in a given metric system

    >>> metric.conversion('G', 'mks')
    Conversion('G', 'T', 0.0001)
    """
    try:
        result = convert(
            str(source),
            str(target),
            quantity=kwargs.get('quantity'),
        )
    except _exceptions.UnitConversionError as err:
        if kwargs.get('error', True):
            raise err
        return
    return Conversion(result.u0, result.u1, float(result))


