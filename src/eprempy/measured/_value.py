from .. import real
from ._context import Context
from ._object import (
    Object,
    ObjectT,
)


class Value(Object[real.ValueType]):
    """A measured object with a single value.

    See Also
    --------
    `~Object`
        An object with real-valued data and an associated unit.
    """

    def __init__(
        self,
        data: real.ValueType,
        context: Context[ObjectT],
        /,
    ) -> None:
        super().__init__(data, context)

    def __int__(self) -> int:
        """Called for int(self)."""
        return int(self.data)

    def __float__(self) -> float:
        """Called for float(self)."""
        return float(self.data)

    def __complex__(self) -> complex:
        """Called for complex(self)."""
        return complex(float(self))


