"""
Support for metric units.
"""

import contextlib
import numbers
import typing

from .. import aliased
from .. import exceptions
from .. import symbolic
from . import _conversions
from . import _defined
from . import _dimensions
from . import _exceptions
from . import _reference


T = typing.TypeVar('T')


class Unit(symbolic.Expression):
    """A symbolic expression representing a physical unit."""

    def __init__(self, terms: typing.List[symbolic.Term]) -> None:
        super().__init__(terms)
        self._dimensions = None
        self._decomposed = None
        self._dimensionless = None
        self._quantity = None
        self._norms = dict.fromkeys(_reference.SYSTEMS)

    def normalize(self, system: str, quantity: str=None):
        """Represent this unit in base units of `system`.

        This is an instance-method version of `~normalize`. See that function
        for full documentation.
        """
        return normalize(self, system, quantity)

    def __mul__(self, other):
        """Called for self * other."""
        if isinstance(other, numbers.Real):
            if other == 1:
                return self
            raise ValueError(f"Cannot compute {self!r} * {other}") from None
        if self is other or super().__eq__(other):
            return unit_factory(super().__pow__(2))
        return _apply_operator(symbolic.product, self, other)

    def __rmul__(self, other):
        """Called for other * self."""
        if isinstance(other, numbers.Real):
            if other == 1:
                return self
            raise ValueError(f"Cannot compute {other} * {self!r}") from None
        return _apply_operator(symbolic.product, other, self)

    def __truediv__(self, other):
        """Called for self / other."""
        if isinstance(other, numbers.Real):
            if other == 1:
                return self
            raise ValueError(f"Cannot compute {self!r} / {other}") from None
        if self is other or super().__eq__(other):
            return unit_factory(1)
        return _apply_operator(symbolic.ratio, self, other)

    def __rtruediv__(self, other):
        """Called for other / self."""
        if isinstance(other, numbers.Real):
            if other == 1:
                return _apply_operator(symbolic.ratio, '1', self)
            raise ValueError(f"Cannot compute {other} / {self!r}") from None
        return _apply_operator(symbolic.ratio, other, self)

    def __pow__(self, other):
        """Called for self ** other."""
        if not isinstance(other, numbers.Real):
            return NotImplemented
        return unit_factory([term ** other for term in self])

    def __rpow__(self, other):
        """Called for other ** self."""
        return NotImplemented

    def __rshift__(self, other):
        """Compute the numerical factor to convert this unit to `other`.

        Examples
        --------
        Create two unit objects representing a meter and a centimeter, and
        compute their relative magnitude::

        >>> m = Unit('m')
        >>> cm = Unit('cm')
        >>> cm >> m
        0.01
        >>> m >> cm
        100.0

        As with `~metric._defined.NamedUnit`, these results are equivalent to
        the statement that there are 100 centimeters in a meter. However, this
        class also supports more complex unit expressions, and can therefore
        compute more complex ratios::

        >>> Unit('g * m^2 / s^2') >> Unit('kg * m^2 / s^2')
        0.001
        >>> Unit('g * mm^2 / s^2') >> Unit('kg * m^2 / s^2')
        1e-09
        >>> Unit('g * m^2 / day^2') >> Unit('kg * m^2 / s^2')
        1.3395919067215364e-13
        >>> Unit('g * au^2 / day^2') >> Unit('kg * m^2 / s^2')
        2997942777.7207007
        """
        if not isinstance(other, (str, Unit)):
            return NotImplemented
        return float(_conversions.conversion_factory(str(self), str(other)))

    def __rrshift__(self, other):
        """Reflected version of `__rshift__`."""
        if isinstance(other, str):
            return float(_conversions.conversion_factory(other, str(self)))
        return NotImplemented

    def __lshift__(self, other):
        """Compute the numerical factor to convert `other` to this unit."""
        if not isinstance(other, (str, Unit)):
            return NotImplemented
        return float(_conversions.conversion_factory(str(other), str(self)))

    def __rlshift__(self, other):
        """Reflected version of `__lshift__`."""
        if isinstance(other, str):
            return float(_conversions.conversion_factory(str(self), other))
        return NotImplemented

    def __eq__(self, other) -> bool:
        """Called for self == other.

        Two unit expressions are equal if they satisfy one of the following
        conditions:

        1. are identical
        1. have symbolically equal strings
        1. have symbolically equivalent strings

        For example, all of the following are true:

        * `Unit('N') == Unit('N')` (condition 1)
        * `Unit('m / s') == 'm / s'` (condition 2)
        * `'m / s' == Unit('m / s')` (condition 2)
        * `Unit('m / s') == 'm s^-1'` (condition 3)
        * `'m / s' == Unit('m s^-1)'` (condition 3)

        See Also
        --------
        `__and__`:
            Test equivalence of two unit expressions.
        `__or__`:
            Test consistency of two unit expressions.
        """
        if other is self:
            # If they are identical, they are equal.
            return True
        # Otherwise, they are equal iff their symbolic expressions are equal.
        return super().__eq__(other)

    def __and__(self, other):
        """Called for self & other.

        This method tests whether the given unit is equivalent to this unit. Two
        unit expressions are are equivalent if they satisfy one of the following
        conditions:

        1. are equal (see docstring at `__eq__`)
        1. differ only by dimensionless terms
        1. have a ratio of unity

        For example, all of the following are true:

        * `Unit('1 / s') & '# / s'` (condition 2)
        * `'1 / s' & Unit('# / s')` (condition 2)
        * `Unit('N') & 'kg * m / s^2'` (condition 3)
        * `'N' & Unit('kg * m / s^2')` (condition 3)

        Equivalence thus defines a notion of equality that does not require two
        unit expressions that represent equal physical quantities to have equal
        lexical representations.
        """
        if self == other:
            return True
        unity = (
            str(term) in _reference.UNITY
            for term in self.difference(other, symmetric=True)
        )
        if all(unity):
            # If the only terms that differ between the units are dimensionless
            # terms, we can declare them equal by inspection (i.e., without
            # computing their conversion factor).
            return True
        that = unit_factory(other)
        if self.dimensionless != that.dimensionless:
            # If one, and only one, of the units is dimensionless, they can't
            # possibly be equivalent.
            return False
        if set(self.decomposed) == set(that.decomposed):
            # If their base units are equal, the units are equivalent.
            return True
        if symbolic.equality(self.decomposed, that.decomposed):
            # If their base units produce equal expressions, the units are
            # equivalent.
            return True
        with contextlib.suppress(_exceptions.UnitConversionError):
            # If their numerical conversion factor is unity, they are
            # equivalent.
            return self << that == 1.0
        return False

    __rand__ = __and__
    """Called for other & self.

    Notes
    -----
    This is the reflected version of `~metric.Unit.__and__`. It exists to
    support equivalence comparisons between instances of `~metric.Unit` and
    objects of other types for which that comparison is meaningful, in cases
    where the other object is the left operand. The semantics are identical.
    """

    def __or__(self, other):
        """Called for self | other.

        This method tests whether the given unit is metrically consistent with
        this unit. Two units are metrically consistent if they satisfy one of
        the following conditions:

        1. are equal (see docstring at `__eq__`)
        1. are equivalent (see docstring at `__and__`)
        1. have the same dimension in at least one metric system
        1. have a defined conversion factor

        For example, all of the following are true:

        * `Unit('J') | 'erg'` (condition 3)
        * `'J' | Unit('erg')` (condition 3)
        * `Unit('J') | 'eV'` (condition 4)
        * `'J' | Unit('eV')` (condition 4)

        Consistency thus provides a way to determine if this unit can convert to
        the given unit without necessarily attempting the conversion.
        """
        if self == other or self & other:
            return True
        that = unit_factory(other)
        for system in _reference.SYSTEMS:
            defined = self.dimensions[system]
            given = that.dimensions.values()
            if defined and any(d == defined for d in given):
                return True
        if _equivalent_quantities(self, that):
            return True
        try:
            self << that
        except _exceptions.UnitConversionError:
            return False
        else:
            return True

    __ror__ = __or__
    """Called for other | self.

    Notes
    -----
    This is the reflected version of `~metric.Unit.__or__`. It exists to support
    consistency comparisons between instances of `~metric.Unit` and objects of
    other types for which that comparison is meaningful, in cases where the
    other object is the left operand. The semantics are identical.
    """

    @property
    def quantity(self):
        """A symbolic expression of this unit's metric quantity."""
        if self._quantity is None:
            self._quantity = _defined.get_quantity(self)
        return self._quantity

    @property
    def dimensionless(self):
        """True if this unit's dimension is '1' in all metric systems.
        
        Notes
        -----
        This property exists as a convenient shortcut for comparing this unit's
        dimension in each metric system to '1'. If you want to check whether
        this unit is dimensionless in a specific metric system, simply check the
        `dimensions` property for that system.
        """
        if self._dimensionless is None:
            self._dimensionless = all(
                dimension == '1'
                for dimension in self.dimensions.values()
            )
        return self._dimensionless

    @property
    def dimensions(self):
        """The physical dimension of this unit in each metric system."""
        if self._dimensions is None:
            guard = exceptions.Wrapper(self._dimensions_in)
            guard.catch(ValueError)
            mapping = {s: guard.compute(s) for s in _reference.SYSTEMS}
            self._dimensions = _dimensions.Dimensions(**mapping)
        return self._dimensions

    def _dimensions_in(self, system: typing.Literal['mks', 'cgs']):
        """Internal helper for `dimensions` property."""
        expression = symbolic.expression('1')
        systems = set()
        for term in self:
            named = _defined.NamedUnit(term.base)
            allowed = named.systems['allowed']
            dimension = (
                named.dimensions[system] if len(allowed) > 1
                else named.dimensions[allowed[0]]
            )
            expression *= symbolic.expression(dimension) ** term.exponent
            systems.update(allowed)
        if system in systems:
            return _dimensions.Dimension(expression)
        raise ValueError(
            f"Can't define dimension of {self!r} in {system!r}"
        ) from None

    @property
    def decomposed(self):
        """This unit's decomposition into base units, where possible."""
        if self._decomposed is None:
            self._decomposed = _decompose_unit(self)
        return self._decomposed


def _apply_operator(f, a, b):
    """Compute `f(a, b)` where at least `a` or `b` is a `~Unit`.

    This method will attempt to reduce each operand into base units before
    computing the result, in order to reduce the result as much as possible
    """
    if unitlike(a) and unitlike(b):
        return unit_factory(f(_decompose_unit(a), _decompose_unit(b)))
    if isinstance(a, Unit) and isinstance(b, numbers.Real):
        return unit_factory(f(a.decomposed, b))
    if isinstance(a, numbers.Real) and isinstance(b, Unit):
        return unit_factory(f(a, b.decomposed))
    return NotImplemented


def _decompose_unit(unit: typing.Union[str, Unit]):
    """Decompose the given unit into base units where possible."""
    decomposed = [
        part
        for term in symbolic.expression(unit)
        for part in _decompose_term(term)
    ]
    return symbolic.reduce(decomposed)


def _decompose_term(term: symbolic.Term):
    """Decompose a symbolic term into named units, if possible."""
    try:
        # Possible outcomes
        # - success: returns list of terms
        # - decomposition failed: returns `None`
        # - parsing failed: raises `UnitParsingError`
        # - metric system is ambiguous: raises `SystemAmbiguityError`
        current = _defined.NamedUnit(term.base).decomposed
    except (_exceptions.UnitParsingError, _exceptions.SystemAmbiguityError):
        # This effectively reduces the three failure modes listed above into
        # one result.
        current = None
    if current is None:
        # If the attempt to decompose this unit term failed or raised an
        # exception, our only option is to append the existing term to the
        # running list.
        return [term]
    # If the attempt to decompose this unit term succeeded, we need to
    # distribute the term's exponent over the new terms and append each to
    # the running list.
    return [base**term.exponent for base in current]


_units = aliased.MutableMapping()
"""Internal collection of singleton `~Unit` instances."""

def unit_factory(arg: typing.Union[str, Unit]) -> Unit:
    """Create a metric unit representing the given expression."""
    if isinstance(arg, Unit):
        return arg
    # Attempt to extract a string representing a single unit.
    if isinstance(arg, str):
        string = arg
    else:
        try:
            string = str(arg[0]) if len(arg) == 1 else None
        except TypeError:
            string = None
    if available := _units.get(string):
        # If the argument maps to an existing unit, return that unit.
        return available
    # First time through: create a symbolic expression from `arg`.
    expression = symbolic.expression(arg)
    # The canonical string representation of this unit is the expression
    # string of its unit symbols. For example, both 'm / s' and 'meter /
    # second' should map to 'm / s'.
    symbols = [_as_symbol(term) for term in expression]
    instance = Unit(symbols)
    name = str(instance)
    if name in _units:
        # It turns out that the argument corresponds to an existing unit.
        existing = _units[name]
        if isinstance(arg, str):
            # If the argument is a string, register the argument as an alias
            # for that unit so we can just retrieve it next time.
            _units.alias(name, arg)
        return existing
    # Create the initial mapping aliases for this unit.
    try:
        # If `name` corresponds to a named unit, register both the name and
        # symbol (e.g., 'centimeter' and 'cm').
        this = _defined.NamedUnit(name)
        key = (this.name, this.symbol)
    except _exceptions.UnitParsingError:
        # If attempting to parse a named unit from `name` failed, register
        # the canonical string and, if applicable, the string argument.
        key = (name, string) if string else name
    # Store and return the new instance.
    _units[key] = instance
    return instance


def normalize(
    unit: typing.Union[str, Unit],
    system: str,
    quantity: str=None,
) -> Unit:
    """Represent a unit in base units of `system`.
    
    Parameters
    ----------
    unit : string or `~Unit`
        The original unit. If `unit` is a string, this function will first
        convert it to an instance of `~Unit`.

    system : string
        The metric system in which to express the result.

    quantity : string, optional
        The physical quantity associated with `unit`. If `quantity` is omitted,
        this function will compute a suitable quantity from the base units of
        `unit`. Providing an explicit quantity may resolve ambiguity in certain
        cases (e.g., between 'velocity' and 'conductance' in CGS).

    Returns
    -------
    `~Unit`
    """
    this = unit_factory(unit)
    terms = (
        _defined.get_quantity(this) if quantity is None
        else symbolic.expression(quantity)
    )
    expression = [
        symbolic.power(_defined.UNITS[term.base][system], term.exponent)
        for term in terms
    ]
    return unit_factory(expression)


def _as_symbol(unit: symbolic.Term):
    """Represent `unit` in terms of its symbol."""
    this = _reference.NAMED_UNITS[unit.base]
    prefix = this['prefix']['symbol']
    base = this['base']['symbol']
    return symbolic.term(prefix + base) ** unit.exponent


def _equivalent_quantities(u0: Unit, u1: Unit):
    """True if two units have equivalent physical quantities."""
    try:
        q0 = _defined.get_quantity(u0)
        q1 = _defined.get_quantity(u1)
    except Exception:
        # NOTE: This is the same pattern that `numpy.array_equal` uses.
        # Basically, if anything goes wrong while trying to compute the physical
        # quantity of either unit, we give up and declare them not equivalent.
        return False
    return q0 == q1


UnitType = typing.TypeVar('UnitType', Unit, symbolic.Expressable)
"""Type variable for unit-like objects.

A unit-like object is an object that can represent a metric unit, if it
corresponds to a known metric unit. Formally, it is an object that can
instantiate the `~metric.Unit` class. This definition makes no guarantee that
the resulting instance will be valid.

See Also
--------
`~metric.UnitLike`
    The equivalent type alias.
`~metric.unitlike`
    The corresponding instance test.
"""


UnitLike = typing.Union[Unit, symbolic.Expressable]
"""Type alias for unit-like objects.

A unit-like object is an object that can represent a metric unit, if it
corresponds to a known metric unit. Formally, it is an object that can
instantiate the `~metric.Unit` class. This definition makes no guarantee that
the resulting instance will be valid.

See Also
--------
`~metric.UnitType`
    The equivalent type variable.
`~metric.unitlike`
    The corresponding instance test.
"""


def unitlike(this):
    """True if `this` can serve as a metric unit.
    
    Notes
    -----
    This function will return `True` if `this` is

    * an instance of `~metric.Unit` or `str`, or one of their subclasses
    * a strict instance of `~symbolic.Expression`

    The justification for the restriction in the latter case is to avoid a false
    positive when `this` is a `~metric` subclass of `~symbolic.Expression`
    (e.g., `~metric.Dimension`).

    See Also
    --------
    `~metric.UnitType`
        The type variable for unit-like objects.
    `~metric.UnitLike`
        The type alias for unit-like objects.
    """
    return (
        isinstance(this, (Unit, str))
        or type(this) is symbolic.Expression
    )


def reduction(unit: symbolic.Expressable, system: str=None):
    """Reduce the given unit expression, if possible.
    
    Notes
    -----
    This function is still experimental.
    """
    expression = symbolic.expression(unit)
    decomposed = []
    for term in expression:
        try:
            # NOTE: `_defined.NamedUnit.reduce` can return `None`
            current = _defined.NamedUnit(term.base).reduce(system=system)
        except (_exceptions.UnitParsingError, _exceptions.SystemAmbiguityError):
            current = None
        if current:
            decomposed.append(current**term.exponent)
    if not decomposed:
        return
    result = decomposed[0]
    for other in decomposed[1:]:
        result *= other.scale
    return result


