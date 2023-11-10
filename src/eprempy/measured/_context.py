"""
Initialization contexts for measured objects.
"""

import typing

from .. import etc
from .. import metric


T = typing.TypeVar('T')

Converter = typing.Callable[[metric.Conversion, T], T]


@etc.autostr
class Context(typing.Generic[T]):
    """Concrete context for objects with a metric unit."""

    def __init__(
        self,
        unit: metric.UnitLike,
        converter: Converter[T],
        /,
    ) -> None:
        self._unit = unit
        self._converter = converter

    def convert(self, x: T, new: metric.UnitLike) -> T:
        """Convert the given object to a new unit.

        Parameters
        ----------
        x : `~T`
            The object to convert.
        new : unit-like
            The unit to which to convert `x`.

        Returns
        -------
        `~T`
            The original object or an object with the same type.

        Raises
        ------
        `ValueError`
            The proposed unit is inconsistent with the given object's current
            unit. Two units are consistent if they have the same dimension in a
            known metric system.
        """
        if metric.unitlike(new):
            try:
                c = metric.conversion(self.unit, new)
            except metric.UnitConversionError as err:
                if not (self.unit | new):
                    raise ValueError(
                        f"The unit {str(new)!r} is inconsistent"
                        f" with {str(self.unit)!r}"
                    ) from err
                raise err
            return self.apply(c, x)
        raise TypeError(
            f"Cannot interpret {new!r} as a unit"
        ) from None

    @property
    def unit(self):
        """The metric unit associated with this context."""
        return self._unit

    def apply(self, c: metric.Conversion, x: T) -> T:
        """Apply the given unit conversion to the given object."""
        return self.converter(c, x)

    @property
    def converter(self):
        """The unit-conversion application."""
        return self._converter


@typing.overload
def context_factory(
    unit: metric.UnitLike=typing.Literal['1'],
    converter: typing.Optional[Converter[T]]=None,
) -> Context[T]: ...

def context_factory(*args, **kwargs):
    """Factory function for `~Context`."""
    try:
        unit, converter = context_args(*args, **kwargs)
    except (TypeError, ValueError) as err:
        argstr = ', '.join(str(arg) for arg in args)
        kwdstr = ', '.join(f"{k}={v}" for k, v in kwargs.items())
        callstr = f"{argstr}, {kwdstr}" if kwdstr else argstr
        raise TypeError(
            f"Failed to initialize a context from ({callstr})"
        ) from err
    return Context(unit, converter)


def context_args(*args, **kwargs) -> typing.Tuple[metric.Unit, Converter[T]]:
    """Parse arguments to initialize an instance of `~Context`."""
    if args and not kwargs:
        return metric.unit(args[0] or '1'), args[1] or _default_converter
    if kwargs and not args:
        return (
            metric.unit(kwargs.get('unit') or '1'),
            kwargs.get('converter') or _default_converter,
        )
    if len(args) == 1:
        return (
            metric.unit(args[0] or '1'),
            kwargs.get('converter') or _default_converter,
        )
    message = f"{args}, {', '.join(f'{k}={v}' for k, v in kwargs.items())}"
    raise TypeError(message)


def _default_converter(c: metric.Conversion, x: T) -> T:
    """Default scaling function for unit conversion."""
    return type(x)(float(c) * x)


