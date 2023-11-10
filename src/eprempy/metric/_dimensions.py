"""
Support for metric dimensions.
"""

import typing

from .. import etc
from .. import symbolic
from . import _defined
from . import _reference


Instance = typing.TypeVar('Instance', bound='Dimension')


class Dimension(symbolic.Expression):
    """An symbolic expression representing a physical dimension."""

    def __init__(self, arg: symbolic.Expressable) -> None:
        super().__init__(arg)
        self._quantities = {}

    def quantities(self, system: str) -> typing.Set[str]:
        """The quantities with this dimension in `system`."""
        if system in self._quantities:
            return self._quantities[system]
        canonical = _defined.CANONICAL['dimensions'][system]
        found = {k for k, v in canonical.items() if v == self}
        self._quantities[system] = found
        return found


def dimension_factory(arg: symbolic.Expressable):
    """Factory function for metric dimensions."""
    return Dimension(symbolic.expression(arg))


@etc.autostr
class Dimensions(typing.Mapping):
    """A collection of symbolic expressions of metric dimensions."""

    def __init__(
        self,
        common: symbolic.Expressable=None,
        **systems: symbolic.Expressable
    ) -> None:
        """Initialize from expressable quantities.
        
        Parameters
        ----------
        common : string or iterable or `~symbolic.Expression`
            The dimension to associate with all metric systems.

        **systems
            Zero or more key-value pairs in which the key is the name of a known
            metric system and the value is an object that can instantiate the
            `~symbolic.Expression` class. If present, each value will override
            `common` for the corresponding metric system.
        """
        self._objects = self._init_from(common, **systems)

    def _init_from(
        self,
        common,
        **systems
    ) -> typing.Dict[str, typing.Optional[Dimension]]:
        """Create dimension objects from arguments."""
        created = dict.fromkeys(_reference.SYSTEMS)
        default = Dimension(common) if common else None
        updates = {
            system: Dimension(expressable) if expressable else default
            for system, expressable in systems.items()
        }
        created.update(updates)
        if any(created.values()):
            return created
        raise TypeError(
            f"Can't instantiate {self.__class__!r}"
            f" from {common!r} and {systems!r}"
        ) from None

    def __len__(self) -> int:
        return len(self._objects)

    def __iter__(self) -> typing.Iterator:
        return iter(self._objects)

    def __getitem__(self, __k):
        key = str(__k).lower()
        if key in self._objects:
            return self._objects[key]
        raise KeyError(f"No dimension for {__k!r}") from None

    def __str__(self) -> str:
        return ', '.join(
            f"{k!r}: {str(v) if v else v!r}"
            for k, v in self._objects.items()
        )


