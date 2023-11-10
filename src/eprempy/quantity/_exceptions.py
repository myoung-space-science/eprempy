class ParsingTypeError(TypeError):
    """An argument to `~parse` has an invalid type."""


class ParsingValueError(ValueError):
    """An argument to `~parse` has an invalid value."""


class MeasurementTypeError(TypeError):
    """An object's `__measure__` method did not return a `~Measurement`."""


class MeasuringTypeError(TypeError):
    """An argument to `~measure` has an invalid type."""


