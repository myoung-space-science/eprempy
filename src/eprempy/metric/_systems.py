"""
Support for working with metric systems.
"""

import collections.abc
import typing

from .. import etc
from .. import symbolic
from . import _conversions
from . import _defined
from . import _dimensions
from . import _exceptions
from . import _reference
from . import _units


@etc.autostr
class Properties:
    """Canonical properties of a quantity within a metric system."""

    def __init__(
        self,
        system: str,
        unit: typing.Union[str, _units.Unit],
    ) -> None:
        self._system = system.lower()
        self._unit = _units.unit_factory(unit)
        self._dimension = None

    @property
    def unit(self):
        """The canonical unit of this quantity in this metric system."""
        return self._unit

    @property
    def dimension(self):
        """The dimension of this quantity in this metric system."""
        if self._dimension is None:
            self._dimension = self.unit.dimensions[self._system]
        return self._dimension

    def __eq__(self, __o) -> bool:
        """True if two instances have equal units and dimensions."""
        try:
            equal = [
                getattr(self, attr) == getattr(__o, attr)
                for attr in ('unit', 'dimension')
            ]
            return all(equal)
        except AttributeError:
            return False

    def __str__(self) -> str:
        properties = ', '.join(
            f"{p}={str(getattr(self, p, None))!r}"
            for p in ['unit', 'dimension']
        )
        return f"{properties} [{self._system!r}]"


@etc.autostr
class Quantity:
    """A single metric quantity.

    An instance of this class represents the properties of the named metric
    quantity in all defined metric systems.
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._units = None
        self._dimensions = None

    def __getitem__(self, system: str):
        """Get this quantity's representation in the named metric system."""
        try:
            unit = self.units[system.lower()]
            return Properties(system, unit)
        except KeyError as err:
            raise _exceptions.QuantityError(
                f"No properties available for {self.name!r} in {system!r}"
            ) from err

    def convert(self, unit: str) -> _conversions.Converter:
        """Create a conversion handler for `unit`.

        Parameters
        ----------
        unit : string
            The unit of this quantity from which to convert.

        Returns
        -------
        `~Converter`
            An instance of the unit-conversion handler. The returned object
            supports conversion from `unit` to any unit for which the conversion
            is defined, or to the equivalent unit in a given metric system.

        Notes
        -----
        - This method is defined within the scope of a particular metric
          quantity because unit conversions are only defined relative to their
          respective quantities, even though two quantities may have identical
          conversions (e.g., frequency and vorticity). The distinction between
          quantities is necessary when dealing with CGS electromagnetic units.
          For example, 'cm / s' is the canonical unit of both conductance and
          velocity in CGS; converting to its equivalent MKS unit therefore
          requires knowledge of the relevant quantity.
        """
        return _conversions.converter_factory(unit, self.name)

    _attrs = ('dimensions', 'units')

    def __eq__(self, other) -> bool:
        """Called to test equality via self == other.
        
        Two instances of this class are either identical, in which case they are
        triviall equal, or they represent distinct quantities, in which they are
        not equal. In addition, an instance of this class will compare equal to
        its case-insensitive name.

        See Also
        --------
        `~metric.Quantity.__or__` : test equivalence between quantities.
        """
        if isinstance(other, str):
            return other.lower() == self.name
        return other is self

    def __or__(self, other) -> bool:
        """Called to test equivalence via self | other.
        
        Two metric quantities are equivalent if their dimensions are equal in a
        given metric system. This operation thus provides a way to compare
        unequal quantities to determine if they are have a physical
        correspondence. For example, energy and work are distinct quantities,
        but they have identical dimensions and are linked through the
        work-energy theorem.

        This operation is only defined between two instances of this class.
        """
        if isinstance(other, Quantity):
            for system in _reference.SYSTEMS:
                if self[system].dimension != other[system].dimension:
                    return False
            return True
        return NotImplemented

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return self.name

    @property
    def units(self):
        """The unit of this quantity in each metric system."""
        if self._units is None:
            self._units = _defined.UNITS[self.name]
        return self._units

    @property
    def dimensions(self):
        """The dimension of this quantity in each metric system."""
        if self._dimensions is None:
            self._dimensions = _defined.DIMENSIONS[self.name]
        return self._dimensions

    @property
    def name(self):
        """The name of this physical quantity."""
        return self._name


_quantities = {}
"""Internal collection of singleton `~Quantity` instances."""

def quantity_factory(arg: typing.Union[str, Quantity]) -> Quantity:
    """Factory function for metric quantities.

    Parameters
    ----------
    arg : string or `~Quantity`.
        The metric quantity to represent. If `arg` is already an instance of
        `~Quantity`, this function will immediately return it.

    Returns
    -------
    `~Quantity`
    """
    if isinstance(arg, Quantity):
        return arg
    name = str(arg).lower()
    if available := _quantities.get(name):
        return available
    q = Quantity(name)
    _quantities[name] = q
    return q


class SearchError(KeyError):
    """Error while searching for a requested metric."""
    pass


@etc.autostr
class System(collections.abc.Mapping):
    """Representations of physical quantities within a given metric system."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._units = None
        self._dimensions = None

    def __len__(self) -> int:
        """The number of quantities defined in this metric system."""
        return _reference._QUANTITIES.__len__()

    def __iter__(self) -> typing.Iterator:
        """Iterate over defined metric quantities."""
        return _reference._QUANTITIES.__iter__()

    def __getitem__(self, key: typing.Union[str, Quantity]):
        """Get the metric for the requested quantity in this system."""
        try:
            found = quantity_factory(key)
        except ValueError as err:
            raise KeyError(f"No known quantity called '{key}'") from err
        else:
            return found[self.name]

    def get_dimension(self, this: typing.Union[str, _units.Unit]):
        """Compute the dimension of `unit` in this metric system."""
        unit = _units.unit_factory(this)
        expression = symbolic.expression('1')
        systems = set()
        for term in unit:
            named = _defined.NamedUnit(term.base)
            allowed = named.systems['allowed']
            dimension = (
                named.dimensions[self.name] if len(allowed) > 1
                else named.dimensions[allowed[0]]
            )
            expression *= symbolic.expression(dimension) ** term.exponent
            systems.update(allowed)
        if self.name in systems:
            return _dimensions.dimension_factory(expression)
        raise ValueError(
            f"Can't define dimension of {unit!r} in {self.name!r}"
        ) from None

    def get_unit(
        self,
        *,
        unit: typing.Union[str, _units.Unit]=None,
        dimension: typing.Union[str, _dimensions.Dimension]=None,
        quantity: typing.Union[str, Quantity]=None,
    ) -> typing.Optional[_units.Unit]:
        """Get a canonical unit from a given unit, dimension, or quantity.

        This method will search for the unit in the current metric system based
        on `unit`, `dimension`, or `quantity`, in that order. All arguments
        default to `None`. If `unit` is not `None`, this method will attempt to
        return the equivalent canonical unit; if either `dimension` or
        `quantity` is not `None`, this method will attempt to return the unique
        corresponding unit.

        Parameters
        ----------
        unit : string or Unit
            A unit of measure in any system.

        dimension : string or Dimension
            A physical dimension.

        quantity : string or Quantity
            A physical quantity.

        Returns
        -------
        Unit
            The corresponding unit in the current metric system.

        """
        methods = {
            k: getattr(self, f'_unit_from_{k}')
            for k in ('unit', 'dimension', 'quantity')
        }
        targets = {
            'unit': unit,
            'dimension': dimension,
            'quantity': quantity,
        }
        return self._get_unit(methods, targets)

    T = typing.TypeVar('T', str, _units.Unit, _dimensions.Dimension, Quantity)
    T = typing.Union[str, _units.Unit, _dimensions.Dimension, Quantity]

    def _get_unit(
        self,
        methods: typing.Dict[str, typing.Callable[[T], _units.Unit]],
        targets: typing.Dict[str, T],
    ) -> _units.Unit:
        """Search logic for `get_unit`."""
        nonnull = {k: v for k, v in targets.items() if v}
        cases = [(methods[k], v) for k, v in nonnull.items()]
        for (method, arg) in cases:
            if str(arg) == '1':
                return _units.unit_factory(self['identity'].unit)
            if result := method(arg):
                return result
        args = self._format_targets(nonnull)
        errmsg = f"Could not determine unit in {self.name} from {args}"
        raise SearchError(errmsg)

    def _format_targets(self, targets: typing.Dict[str, T]):
        """Format `get_unit` targets for printing."""
        if not targets:
            return "nothing"
        args = [f'{k}={v!r}' for k, v in targets.items()]
        if 0 < len(args) < 3:
            return ' or '.join(args)
        return f"{', '.join(str(arg) for arg in args[:-1])}, or {args[-1]}"

    def _unit_from_unit(
        self,
        target: typing.Union[str, _units.Unit],
    ) -> _units.Unit:
        """Get the canonical unit corresponding to the given unit."""
        unit = _units.unit_factory(target)
        return unit.normalize(self.name)

    def _unit_from_dimension(
        self,
        target: typing.Union[str, _dimensions.Dimension],
    ) -> _units.Unit:
        """Get the canonical unit corresponding to the given dimension."""
        for quantity, dimension in self.dimensions.items():
            if dimension == target:
                return _units.unit_factory(self.units[quantity])

    def _unit_from_quantity(
        self,
        quantity: typing.Union[str, Quantity],
    ) -> _units.Unit:
        """Get the canonical unit corresponding to the given quantity."""
        return _units.unit_factory(self[quantity].unit)

    def __eq__(self, other) -> bool:
        """True if two systems have the same `name` attribute."""
        if isinstance(other, System):
            return self.name == other.name.lower()
        if isinstance(other, str):
            return self.name == other.lower()
        return NotImplemented

    def __bool__(self) -> bool:
        """A defined metric system is always truthy."""
        return True

    def keys(self) -> typing.KeysView[str]:
        return super().keys()

    def values(self) -> typing.ValuesView[Properties]:
        return super().values()

    def items(self) -> typing.ItemsView[str, Properties]:
        return super().items()

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return str(self.name)

    @property
    def units(self):
        """The unit of each physical quantity in the metric system."""
        if self._units is None:
            self._units = _defined.CANONICAL['units'][self.name]
        return self._units

    @property
    def dimensions(self):
        """The dimension of each physical quantity in the metric system."""
        if self._dimensions is None:
            self._dimensions = _defined.CANONICAL['dimensions'][self.name]
        return self._dimensions

    @property
    def name(self):
        """The name of this metric system."""
        return self._name


_systems = {}
"""Internal collection of singleton `~System` instances."""

def system_factory(arg: typing.Union[str, System]) -> System:
    """Factory function for metric-system representations.

    Parameters
    ----------
    arg : string or `~System`.
        The metric system to represent. If `arg` is already an instance of
        `~System`, this function will immediately return it.

    Returns
    -------
    `~System`
    """
    if isinstance(arg, System):
        return arg
    name = str(arg).lower()
    if available := _systems.get(name):
        return available
    s = System(name)
    _systems[name] = s
    return s


