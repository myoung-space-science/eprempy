"""
Exception classes for the `metric` namespace.

Exceptions defined here:

- `UnitParsingError`
- `UnitConversionError`
- `SystemAmbiguityError`
- `UnitSystemError`
- `QuantityError`
"""


class UnitParsingError(Exception):
    """Error when attempting to parse string into unit."""

    def __init__(self, string: str) -> None:
        self.string = string

    def __str__(self) -> str:
        return f"Could not determine unit and magnitude of '{self.string}'"


class UnitConversionError(Exception):
    """Unknown unit conversion."""


class SystemAmbiguityError(Exception):
    """The metric system is ambiguous."""


class UnitSystemError(Exception):
    """The metric system does not contain this unit."""


class QuantityError(Exception):
    """An error occurred in `~metric.Quantity`."""


