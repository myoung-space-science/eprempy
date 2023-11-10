import abc
import collections.abc
import contextlib
import numbers
import typing

from .. import aliased
from .. import etc
from .. import symbolic
from . import _exceptions
from . import _reference


Instance = typing.TypeVar('Instance', bound='_Property')


@etc.autostr
class _Property(collections.abc.Mapping):
    """All definitions of a single metric property."""

    _instances = {}
    _supported = (
        'dimensions',
        'units',
    )

    key: str=None
    _cache: dict=None

    def __new__(
        cls: typing.Type[Instance],
        arg: typing.Union[str, Instance],
    ) -> Instance:
        """Create a new instance or return an existing one.
        
        Parameters
        ----------
        arg : string or instance
            A string representing the metric property to create, or an existing
            instance of this class.
        """
        if isinstance(arg, cls):
            return arg
        key = str(arg)
        if key not in cls._supported:
            raise ValueError(f"Unsupported property: {key}") from None
        if available := cls._instances.get(key):
            return available
        self = super().__new__(cls)
        self.key = key
        self._cache = {}
        cls._instances[key] = self
        return self

    def system(self, system: str):
        """Get all definitions of this property for `system`."""
        return {k: v[system] for k, v in self.items()}

    LEN = len(_reference._QUANTITIES) # No need to compute every time.

    def __len__(self) -> int:
        """The number of defined quantities. Called for len(self)."""
        return self.LEN

    def __iter__(self) -> typing.Iterator[str]:
        """Iterate over names of defined quantities. Called for iter(self)."""
        return iter(_reference._QUANTITIES)

    def __getitem__(self, quantity: str) -> typing.Dict[str, str]:
        """Create or retrieve a named property."""
        if quantity in self._cache:
            return self._cache[quantity]
        if new := self._get_property(quantity):
            self._cache[quantity] = new
            return new
        raise KeyError(f"Unknown quantity {quantity}") from None

    def _get_property(self, quantity: str) -> typing.Dict[str, str]:
        """Get this property for a defined quantity.
        
        This method will search for `quantity` in the module-level collection of
        defined quantities. If it doesn't find an entry, it will attempt to
        parse `quantity` into known quantities. If it finds a `dict` entry, it
        will attempt to extract the values corresponding to this property's
        `key` attribute (i.e., 'units' or 'dimensions'). If it finds a `str`
        entry, it will attempt to create the equivalent `dict` by symbolically
        evaluating the terms in the entry.
        """
        if quantity not in _reference._QUANTITIES:
            return self._parse(quantity)
        q = _reference._QUANTITIES[quantity]
        if isinstance(q, dict):
            return q.get(self.key, {})
        if not isinstance(q, str):
            raise TypeError(f"Expected {quantity} to be a string") from None
        return self._parse(q)

    def _parse(self, string: str):
        """Parse a string representing a compound quantity."""
        for k in _reference._QUANTITIES:
            string = string.replace(k, k.replace(' ', '_'))
        parts = [
            self._expand(term)
            for term in symbolic.expression(string)
        ]
        keys = {key for part in parts for key in part.keys()}
        merged = {key: [] for key in keys}
        for part in parts:
            for key, value in part.items():
                merged[key].append(value)
        return {
            k: str(symbolic.expression(v))
            for k, v in merged.items()
        }

    _operand = symbolic.OperandFactory()
    def _expand(self, term: symbolic.Term):
        """Create a `dict` of operands from this term."""
        return {
            k: self._operand.create(v, term.exponent)
            for k, v in self[term.base.replace('_', ' ')].items()
        }

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return self.key


# NOTE: Defining mappings from unit or dimension to quantity is a bad idea
# because some quantities have the same unit or dimension in a given system.
# This makes the mapping ill-defined. Python dictionaries simply use the latest
# entry for a repeated key, which means some quantities would overwrite others.
# The following objects rely on mappings from quantity to unit or dimension,
# which are always well defined.


DIMENSIONS = _Property('dimensions')
"""All defined metric dimensions.

This mapping is keyed by physical quantity followed by metric system.
"""


UNITS = _Property('units')
"""All defined metric units.

This mapping is keyed by physical quantity followed by metric system.
"""


CANONICAL = {
    k: {
        system: _Property(k).system(system) for system in ('mks', 'cgs')
    } for k in ('dimensions', 'units')
}
"""Canonical metric properties in each known metric system.

This mapping is keyed by {'dimensions', 'units'}, followed by metric system, and
finally by physical quantity.
"""


MKS = {k: CANONICAL[k]['mks'].copy() for k in ('dimensions', 'units')}
"""All defined units in the MKS system, keyed by physical quantity."""


CGS = {k: CANONICAL[k]['cgs'].copy() for k in ('dimensions', 'units')}
"""All defined units in the CGS system, keyed by physical quantity."""


_EQUIVALENT = {
    p: {
        k: {
            s: symbolic.expression(x)
            for s, x in v.items()
        } for k, v in dict(_Property(p)).items()
    } for p in ('dimensions', 'units')
}

EQUIVALENT = aliased.Mapping(_EQUIVALENT)


class Prefix(typing.NamedTuple):
    """Metadata for a metric order-of-magnitude prefix."""

    symbol: str
    name: str
    factor: float


class BaseUnit(typing.NamedTuple):
    """Metadata for a named unit without metric prefix."""

    symbol: str
    name: str
    quantity: str


Instance = typing.TypeVar('Instance', bound='NamedUnit')


class _NamedUnitMeta(abc.ABCMeta):
    """Internal metaclass for `~metric.NamedUnit`.
    
    This class exists to create singleton instances of `~metric.NamedUnit`
    without needing to overload `__new__` on that class or its base class(es).
    """

    _instances = aliased.MutableMapping()
    _attributes = {}

    def __call__(
        cls,
        arg: typing.Union[Instance, symbolic.Expressable],
    ) -> Instance:
        """Create a new instance or return an existing one."""
        if isinstance(arg, cls):
            # If the argument is already an instance, return it.
            return arg
        string = str(arg)
        if available := cls._instances.get(string):
            # If the argument maps to an existing unit, return that unit.
            return available
        # First time through: identify the base unit and prefix.
        magnitude, reference = identify(string)
        # Store the information to initialize a new instance.
        name = f"{magnitude.name}{reference.name}"
        symbol = f"{magnitude.symbol}{reference.symbol}"
        cls._attributes[string] = {
            'prefix': magnitude,
            'base': reference,
            'name': name,
            'symbol': symbol,
            'scale': magnitude.factor,
            'quantity': reference.quantity,
        }
        # Create the new instance. This will ultimately pass control to
        # `NamedUnit.__init__`, which will initialize the newly instantiated
        # instance with the stored attributes corresponding to `str(arg)`.
        instance = super().__call__(arg)
        cls._instances[(name, symbol)] = instance
        return instance


def identify(string: str):
    """Determine the magnitude and reference unit, if possible.
    
    Parameters
    ----------
    string : str
        A string representing a metric unit.

    Returns
    -------
    tuple
        A 2-tuple in which the first element is a `~metric.Prefix` representing
        the order-of-magnitude of the given unit and the second element is a
        `~metric.BaseUnit` representing the unscaled (i.e., order-unity) metric
        unit.

    Examples
    --------
    >>> mag, ref = identify('km')
    >>> mag
    Prefix(symbol='k', name='kilo', factor=1000.0)
    >>> ref
    BaseUnit(symbol='m', name='meter', quantity='length')
    """
    try:
        unit = _reference.NAMED_UNITS[string]
    except KeyError as err:
        raise _exceptions.UnitParsingError(string) from err
    magnitude = Prefix(**unit['prefix'])
    reference = BaseUnit(**unit['base'])
    return magnitude, reference


@etc.autostr
class Reduction:
    """The components of a reduced unit expression."""

    def __init__(
        self,
        terms: symbolic.Expressable,
        scale: float=1.0,
        system: str=None,
    ) -> None:
        self._expression = scale * symbolic.expression(terms)
        self.system = system
        self.scale = scale
        self._units = None

    @property
    def units(self) -> typing.List[symbolic.Term]:
        """The unit terms in this reduction."""
        if self._units is None:
            self._units = [
                unit for unit in self._expression.terms
                if unit.base != '1'
            ]
        return self._units

    def __mul__(self, other):
        """Called for self * other."""
        if not isinstance(other, numbers.Real):
            return NotImplemented
        scale = self.scale * other
        terms = list(scale * self._expression)
        return type(self)(terms, scale=scale, system=self.system)

    __rmul__ = __mul__
    """Called for other * self."""

    def __truediv__(self, other):
        """Called for self / other."""
        if not isinstance(other, numbers.Real):
            return NotImplemented
        scale = self.scale / other
        terms = list(scale * self._expression)
        return type(self)(terms, scale=scale, system=self.system)

    def __pow__(self, other):
        """Called for self ** other."""
        if not isinstance(other, numbers.Real):
            return NotImplemented
        scale = self.scale ** other
        terms = list(scale * self._expression**other)
        return type(self)(terms, scale=scale, system=self.system)

    def __str__(self) -> str:
        return f"{self._expression} [{self.system!r}]"


@etc.autostr
class NamedUnit(metaclass=_NamedUnitMeta):
    """A single named unit and corresponding metadata."""

    @typing.overload
    def __init__(
        self: Instance,
        unit: str,
    ) -> Instance:
        """Create a new instance or return an existing one.
        
        Parameters
        ----------
        unit : string
            A string representing the metric unit to create.
        """

    @typing.overload
    def __init__(
        self: Instance,
        instance: Instance,
    ) -> Instance:
        """Create a new instance or return an existing one.
        
        Parameters
        ----------
        instance : `~metric.NamedUnit`
            An existing instance of this class.
        """

    def __init__(self, arg) -> None:
        self._parsed = self.__class__._attributes[str(arg)]
        self._prefix = None
        self._base = None
        self._name = None
        self._symbol = None
        self._scale = None
        self._quantity = None
        self._systems = None
        self._dimensions = None
        self._decomposed = None
        self._norm = None
        self._reductions = dict.fromkeys(_reference.SYSTEMS)

    @property
    def norm(self):
        """The equivalent unit, represented in base units of `system`.
        
        Notes
        -----
        This property returns a copy of the original `dict` of normalized units
        in order to prevent modifying singleton instances.
        """
        if self._norm is None:
            self._norm = {
                system: type(self)(UNITS[self.quantity][system])
                for system in _reference.SYSTEMS
            }
        return self._norm.copy()

    @property
    def prefix(self) -> Prefix:
        """The order of magnitide of this unit's metric prefix."""
        if self._prefix is None:
            self._prefix = self._parsed["prefix"]
        return self._prefix

    @property
    def base(self) -> BaseUnit:
        """The reference unit without metric prefix."""
        if self._base is None:
            self._base = self._parsed["base"]
        return self._base

    @property
    def name(self) -> str:
        """The full name of this unit."""
        if self._name is None:
            self._name = self._parsed["name"]
        return self._name

    @property
    def symbol(self) -> str:
        """The abbreviated symbol for this unit."""
        if self._symbol is None:
            self._symbol = self._parsed["symbol"]
        return self._symbol

    @property
    def scale(self) -> float:
        """The metric scale factor of this unit."""
        if self._scale is None:
            self._scale = self._parsed["scale"]
        return self._scale

    @property
    def quantity(self) -> str:
        """The physical quantity of this unit."""
        if self._quantity is None:
            self._quantity = self._parsed["quantity"]
        return self._quantity

    @property
    def systems(self):
        """The metric systems that use this unit.
        
        This property uses the criteria described in
        `~metric.NamedUnit.is_allowed_in` to build the collection of metric
        systems, most notably that named units not defined in any metric system
        are allowed in all metric systems.
        """
        if self._systems is None:
            modes = {
                k: []
                for k in {'allowed', 'defined', 'fundamental'}
            }
            for system in _reference.SYSTEMS:
                if self.is_fundamental_in(system):
                    modes['fundamental'].append(system)
                if self.is_defined_in(system):
                    modes['defined'].append(system)
                if self.is_allowed_in(system):
                    modes['allowed'].append(system)
            self._systems = {k: tuple(v) for k, v in modes.items()}
        return self._systems.copy()

    @property
    def decomposed(self):
        """The representation of this unit in base units, if possible."""
        if self._decomposed is None:
            with contextlib.suppress(StopIteration):
                system = next(
                    system for system in _reference.SYSTEMS
                    if self.is_fundamental_in(system)
                )
                self._decomposed = self._decompose(system)
        return self._decomposed

    def _decompose(self, system: typing.Literal['mks', 'cgs']):
        """Internal logic for `NamedUnit.decomposed`."""
        if not self.is_defined_in(system):
            # If this unit is not defined in this metric system, we can't
            # decompose it.
            return
        dimension = self.dimensions[system]
        expression = symbolic.expression(dimension)
        if len(dimension) == 1:
            # If this unit's dimension is irreducible, there's no point in going
            # through all the decomposition logic.
            return [symbolic.term(self.symbol)]
        quantities = [
            _reference._BASE_QUANTITIES.find(term.base, unique=True)['name']
            for term in expression
        ]
        units = [
            _reference._QUANTITIES[quantity]['units'][system]
            for quantity in quantities
        ]
        return [
            symbolic.term(base=unit, exponent=term.exponent)
            for unit, term in zip(units, expression)
        ]

    def reduce(self, system: str=None) -> typing.Optional[Reduction]:
        """Convert this unit to base units of `system`, if possible."""
        s = self._resolve_system(system)
        if self._reductions[s]:
            return self._reductions[s]
        result = self._reduce(s)
        self._reductions[s] = result
        return result

    def _resolve_system(self, system: typing.Optional[str]):
        """Determine the appropriate metric system to use, if possible."""
        if isinstance(system, str) and system.lower() in _reference.SYSTEMS:
            # trivial case
            return system.lower()
        systems = [s for s in _reference.SYSTEMS if self.is_fundamental_in(s)]
        if len(systems) == 1:
            # use canonical system if possible
            return systems[0]
        if self.dimensions['mks'] == self.dimensions['cgs']:
            # system-independent: use mks by default
            return 'mks'
        if self.dimensions['mks'] is None:
            # only defined in cgs
            return 'cgs'
        if self.dimensions['cgs'] is None:
            # only defined in mks
            return 'mks'
        # system-dependent but we don't know the system
        raise _exceptions.SystemAmbiguityError(str(self))

    def _reduce(self, system: typing.Literal['mks', 'cgs']):
        """Internal logic for `~NamedUnit.reduce`."""
        if not self.is_defined_in(system):
            # If this unit is not defined in this metric system, we can't reduce
            # it.
            return
        dimension = self.dimensions[system]
        expression = symbolic.expression(dimension)
        if len(expression) == 1:
            # If this unit's dimension is irreducible, there's no point in going
            # through all the reduction logic.
            canonical = CANONICAL['units'][system][self.quantity]
            if self.symbol == canonical:
                # If this is the canonical unit for its quantity in `system`,
                # return it with a scale of unity.
                return Reduction(
                    [symbolic.term(self.symbol)],
                    system=system,
                )
            # If not, return the canonical unit with the appropriate scale
            # factor.
            return Reduction(
                [symbolic.term(canonical)],
                scale=(canonical << self),
                system=system,
            )
        quantities = [
            _reference._BASE_QUANTITIES.find(term.base, unique=True)['name']
            for term in expression
        ]
        units = [
            _reference._QUANTITIES[quantity]['units'][system]
            for quantity in quantities
        ]
        terms = [
            symbolic.term(base=unit, exponent=term.exponent)
            for unit, term in zip(units, expression)
        ]
        return Reduction(terms, scale=self.scale, system=system)

    @property
    def dimensions(self) -> typing.Dict[str, typing.Optional[str]]:
        """The physical dimension of this unit in each metric system.
        
        Notes
        -----
        This property returns a copy of an internal `dict` in order to prevent
        accidentally changing the instance dimensions through an otherwise valid
        `dict` operation. Such changes are irreversible since each
        `~metric.NamedUnit` instance is a singleton.
        """
        if self._dimensions is None:
            systems = {system for system in self.systems['defined']}
            self._dimensions = {
                k: symbolic.expression(v) or None
                for k, v in self._get_dimensions(systems).items()
            }
        return self._dimensions.copy()

    def _get_dimensions(self, systems: typing.Set[str]):
        """Helper for computing dimensions of this named unit.
        
        Notes
        -----
        This method requires the full set of applicable metric systems (rather
        than one system at a time) because it will return all available
        dimensions if either 1) there are no applicable systems, or 2) the set
        of applicable systems is equal to the set of all known systems.
        """
        dimensions = DIMENSIONS[self.quantity]
        if not systems or (systems == _reference.SYSTEMS):
            return dimensions.copy()
        base = dict.fromkeys(_reference.SYSTEMS)
        if len(systems) == 1:
            system = systems.pop()
            base[system] = dimensions[system]
            return base
        raise _exceptions.SystemAmbiguityError

    def is_allowed_in(self, system: typing.Literal['mks', 'cgs']):
        """True if this named unit inter-operates with units in `system`.
        
        A named unit is allowed in some or all metric systems, but never none.
        The reason for this is that a named unit that is not defined in any
        metric system is effectively independent of all metric systems, so
        attempting to restrict its use to a subset of metric systems is
        fruitless.

        See Also
        --------
        `~is_defined_in`
            True if the given metric system formally contains this named unit.

        `~is_fundamental_in`
            True if this named unit is the fundamental unit for its dimension in
            the given metric system.
        """
        systems = {
            s for s in _reference.SYSTEMS if self.is_defined_in(s)
        } or _reference.SYSTEMS
        return system in systems

    def is_defined_in(self, system: typing.Literal['mks', 'cgs']):
        """True if this named unit is defined in `system`."""
        if self.is_fundamental_in(system):
            return True
        canonical = CANONICAL['units'][system][self.quantity]
        with contextlib.suppress(_exceptions.UnitParsingError):
            reference = type(self)(canonical)
            if self.base == reference.base:
                return True
        return False

    def is_fundamental_in(self, system: typing.Literal['mks', 'cgs']):
        """True if this named unit is the canonical unit in `system`."""
        canonical = CANONICAL['units'][system][self.quantity]
        keys = (self.symbol, self.name)
        for key in keys:
            if key == canonical:
                return True
        return False

    def __eq__(self, other) -> bool:
        """True if two representations have equal magnitude and base unit."""
        that = type(self)(other)
        same_magnitude = (self.prefix == that.prefix)
        same_reference = (self.base == that.base)
        return same_magnitude and same_reference

    def __hash__(self) -> int:
        """Called for hash(self). Supports use as mapping key."""
        return hash((self.base, self.prefix))

    def __rshift__(self, other):
        """Compute the conversion factor from this unit to `other`.

        This operation computes the numerical factor necessary to convert a
        quantity in terms of this unit to a quantity in terms of `other`,
        provided both units have the same base unit.

        Examples
        --------
        The result of this operation is equal to the result of `~metric.ratio`:

        >>> metric.ratio('cm', 'm')
        0.01
        >>> metric.NamedUnit('cm') >> 'm'
        0.01
        """
        if isinstance(other, (NamedUnit, str)):
            return ratio(self, other)
        return NotImplemented

    def __rrshift__(self, other):
        """Reflected version of `__rshift__`."""
        if isinstance(other, str):
            return ratio(other, self)
        return NotImplemented

    def __lshift__(self, other):
        """Compute the conversion factor from `other` to this unit.
        
        This operation computes the numerical factor necessary to convert a
        quantity in terms of `other` to a quantity in terms of this unit,
        provided both units have the same base unit.

        Examples
        --------
        The result of this operation is equal to the inverse of the result of
        `~metric.ratio`:

        >>> metric.ratio('cm', 'm')
        0.01
        >>> metric.NamedUnit('cm') << 'm'
        100.0
        """
        if isinstance(other, (NamedUnit, str)):
            return ratio(other, self)
        return NotImplemented

    def __rlshift__(self, other):
        """Reflected version of `__lshift__`."""
        if isinstance(other, str):
            return ratio(self, other)
        return NotImplemented

    def __str__(self) -> str:
        """A printable representation of this unit."""
        return f"'{self.name} | {self.symbol}'"


def ratio(
    this: typing.Union[str, NamedUnit],
    that: typing.Union[str, NamedUnit],
) -> float:
    """Compute the magnitude of `this` relative to `that`.

    Parameters
    ----------
    this : string or `~metric.NamedUnit`
        The reference unit.

    that : string or `~metric.NamedUnit`
        The unit to compare to `this`. Must have the same base unit as `this`.

    Examples
    --------
    The following are all equivalent to the fact that a meter represents 100
    centimeters:

        >>> ratio('meter', 'centimeter')
        100.0
        >>> ratio('centimeter', 'meter')
        0.01
        >>> ratio('m', 'cm')
        100.0
        >>> ratio('cm', 'm')
        0.01

    Attempting this operation between two units with different base units will
    raise an exception,

        >>> ratio('m', 's')
        <raises ValueError>

    even if they represent the same quantity.

        >>> ratio('m', 'au')
        <raises ValueError>

    Therefore, this function is not intended for unit conversion.
    """
    u = [NamedUnit(i) if isinstance(i, str) else i for i in (this, that)]
    if not all(isinstance(i, NamedUnit) for i in u):
        raise TypeError(
            f"Each unit must be an instance of {str!r} or {NamedUnit!r}"
        ) from None
    u0, u1 = u
    if u1 == u0:
        return 1.0
    if u1.base != u0.base:
        units = ' to '.join(f"{i.symbol!r} ({i.name})" for i in u)
        raise ValueError(f"Can't compare {units}") from None
    return u0.scale / u1.scale


def get_quantity(unit: symbolic.Expression):
    """Compute the physical quantity of the given unit."""
    terms = [
        symbolic.term(
            NamedUnit(term.base).quantity.replace(' ', '_')
        ) ** term.exponent
        for term in unit
    ]
    return symbolic.expression(terms)


