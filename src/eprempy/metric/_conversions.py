"""
Internal support for unit conversions.
"""

import typing

from .. import etc
from .. import symbolic
from . import _defined
from . import _exceptions
from . import _reference


class Conversion:
    """The result of a unit conversion."""

    def __init__(self, u0: str, u1: str, factor: float=1.0) -> None:
        self._u0 = u0
        self._u1 = u1
        self._factor = factor

    def __rtruediv__(self, other):
        """Called to convert this conversion to its inverse."""
        if other != 1:
            clsname = self.__class__.__qualname__.lower()
            raise ValueError(
                f"Cannot compute {other} / <{clsname}>"
                f"; use {other} / float(<{clsname}>)"
            ) from None
        return Conversion(self.u1, self.u0, 1.0 / self._factor)

    def __float__(self) -> float:
        """Reduce this instance to its numerical factor via float(self)."""
        if bool(self):
            return self._factor
        raise TypeError("Conversion is undefined") from None

    def __bool__(self):
        """True if this conversion exists."""
        return self._factor is not None

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        attrstr = f"{self.u0!r}, {self.u1!r}, {self._factor}"
        return f"{self.__class__.__qualname__}({attrstr})"

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return f"({self.u0!r} -> {self.u1!r}) == {float(self)}"

    @property
    def u0(self):
        """The unit from which to convert."""
        return self._u0

    @property
    def u1(self):
        """The unit to which to convert."""
        return self._u1


_conversions = {}
"""Internal collection of computed unit conversions.

This module-level collection is a mapping from unit pairs to their corresponding
`~Conversion` instances. It exists to preclude the need to repeatedly compute
a given conversion.
"""

def conversion_factory(u0: str, u1: str) -> Conversion:
    """Compute the conversion from `u0` to `u1`.

    Parameters
    ----------
    u0 : string
        The unit from which to convert.

    u1 : string
        The unit to which to convert.

    Returns
    -------
    `~Conversion`

    Raises
    ------
    `~UnitConversionError`
        All attempts to convert `u0` to `u1` failed.

    Notes
    -----
    - This function will store both the successful conversion and its inverse in
      an internal module-level `dict` so that subsequent requests for the same
      conversion or its inverse do not trigger redundant computation.
    """
    if available := _conversions.get((u0, u1)):
        return available
    c = _convert(u0, u1)
    _conversions[(u0, u1)] = c
    _conversions[(u1, u0)] = 1 / c
    return c


def _convert(u0: str, u1: str):
    """Attempt to compute the conversion from `u0` to `u1`."""
    converters = (
        _convert_as_strings,
        _convert_as_expressions,
    )
    for converter in converters:
        if factor := converter(u0, u1):
            return Conversion(u0, u1, factor)
    raise _exceptions.UnitConversionError(
        f"Cannot convert {u0!r} to {u1!r}"
    ) from None


def _convert_as_strings(u0: str, u1: str) -> typing.Optional[float]:
    """Attempt to convert `u0` to `u1` as strings."""
    checked = []
    if factor := _recursive_conversion(checked, u0, u1):
        return factor


def _recursive_conversion(
    checked: typing.List[str],
    u0: str,
    u1: str,
    scale: float=1.0,
) -> typing.Optional[float]:
    """Attempt to convert `u0` to `u1` as strings."""
    if u0 not in checked:
        checked += [u0]
        if factor := _standard_conversion(u0, u1, scale=scale):
            return factor
        conversions = _reference.CONVERSIONS.get_adjacencies(u0).items()
        for unit, weight in conversions:
            if value := _recursive_conversion(checked, unit, u1, scale=scale):
                return weight * value


def _standard_conversion(
    u0: str,
    u1: str,
    scale: float=1.0,
) -> typing.Optional[float]:
    """Attempt to convert `u0` to `u1` non-recursively.

    This function will attempt to compute the appropriate numerical
    conversion factor via one of the following strategies

    - looking up a defined conversion
    - computing the ratio of metric scale factors
    - transitively scaling through an intermediate conversion
    """
    if factor := _simple_conversion(u0, u1, scale=scale):
        return factor
    if factor := _rescale_conversion(u0, u1, scale=scale):
        return factor


def _convert_as_expressions(u0: str, u1: str):
    """Convert complex unit expressions term-by-term."""
    e0, e1 = (symbolic.expression(unit) for unit in (u0, u1))
    if e0 == e1:
        return 1.0
    terms = [
        term for term in (e0 / e1).terms
        if term.base not in _reference.UNITY
    ]
    if factor := _resolve_terms(terms):
        return factor
    if factor := _convert_by_dimensions(terms):
        return factor


def _simple_conversion(u0: str, u1: str, scale: float=1.0):
    """Attempt to compute a simple conversion from `u0` to `u1`.
    
    This method will attempt the following conversions, in the order listed:
    
    * the identity conversion (i.e., `u0 == u1`);
    * a defined conversion from `u0` to `u1`;
    * the metric ratio of `u1` to `u0` (e.g., `'km'` to `'m'`);

    If it does not succeed, it will return `None` in order to allow other
    methods an opportunity to convert `u0` to `u1`.
    """
    if u0 == u1:
        return scale
    if found := _search(u0, u1):
        return scale * found
    try:
        ratio = _defined.NamedUnit(u0) >> _defined.NamedUnit(u1)
    except (ValueError, _exceptions.UnitParsingError):
        return
    return scale * ratio


def _rescale_conversion(u0: str, u1: str, scale: float=1.0):
    """Attempt to convert `u0` to `u1` via an intermediate unit.

    This method will attempt the following conversions, in the order listed:

    - a defined conversion to `u1` from a unit that has the same base unit as,
      but different metric scale than, `u0` (see `~Conversion._rescale`);
    - the numerical inverse of the above process applied to the conversion from
      `u1` to `u0`;

    If it does not succeed, it will return `None` in order to allow other
    methods an opportunity to convert `u0` to `u1`.
    
    Notes
    -----
    It is possible for `u0` or `u1` to individually be in `CONVERSIONS.nodes`
    even when `(u0, u1)` is not in `CONVERSIONS`. For example, there are nodes
    for both 'min' (minute) and 'd' (day), each with a conversion to 's'
    (second), but there is no direct conversion from 'min' to 'd'.
    """
    if u0 not in _reference.CONVERSIONS.nodes:
        if computed := _rescale(u0, u1):
            return scale * computed
    if u1 not in _reference.CONVERSIONS.nodes:
        if computed := _rescale(u1, u0):
            return scale / computed


def _rescale(u0: str, u1: str):
    """Compute a new conversion after rescaling `u0`.
    
    This method will look for a unit, `ux`, in `~metric.CONVERSIONS` that has
    the same base unit as `u0`. If it finds one, it will attempt to convert `ux`
    to `u1`, and finally multiply the result by the relative magnitude of `u0`
    to `ux`. In other words, it attempts to compute `(u0 << ux) * (ux -> u1)` in
    place of `(u0 -> u1)`.

    For example, if the direct conversion from megajoules to ergs is not
    available but the direct conversions from megajoules to joules and from
    joule to ergs are, this function will attempt to compute `('MJ' -> 'erg') =
    ('MJ' -> 'J') * ('J' -> 'erg')`.
    """
    if not u0 in _reference.NAMED_UNITS:
        return
    n0 = _defined.NamedUnit(u0)
    for ux in _reference.CONVERSIONS.nodes:
        if ux in _reference.NAMED_UNITS:
            nx = _defined.NamedUnit(ux)
            if nx.base == n0.base:
                if found := _search(ux, u1):
                    return (nx << n0) * found


def _search(u0: str, u1: str):
    """Search the defined conversions.
    
    This method will first search for a defined conversion from `u0` to `u1`. If
    it can't find one, it will search for a defined conversion from an alias of
    `u0` to an alias of `u1`. See `~_get_aliases_of` for more information.
    """
    if (u0, u1) in _reference.CONVERSIONS:
        return _reference.CONVERSIONS.get_weight(u0, u1)
    starts = _get_aliases_of(u0)
    ends = _get_aliases_of(u1)
    for ux in starts:
        for uy in ends:
            if (ux, uy) in _reference.CONVERSIONS:
                return _reference.CONVERSIONS.get_weight(ux, uy)


def _get_aliases_of(unit: str):
    """Build a list of possible variations of this unit string.
    
    The aliases of `unit` comprise the given string, as well as the canonical
    name and symbol of the corresponding named unit, if one exists.
    """
    built = [unit]
    if unit in _reference.NAMED_UNITS:
        known = _defined.NamedUnit(unit)
        built.extend([known.symbol, known.name])
    return built


def _convert_by_dimensions(terms: typing.List[symbolic.Term]):
    """Attempt to compute a conversion via unit dimensions."""
    decomposed = []
    for term in terms:
        reduction = _defined.NamedUnit(term.base).reduce()
        if reduction:
            decomposed.extend(
                [
                    symbolic.term(
                        coefficient=reduction.scale**term.exponent,
                        base=this.base,
                        exponent=term.exponent*this.exponent,
                    )
                    for this in reduction.units
                ]
            )
    if symbolic.expression(decomposed) == '1':
        return 1.0
    return _resolve_terms(decomposed)


def _resolve_terms(terms: typing.List[symbolic.Term]):
    """Compute ratios of matching terms, if possible."""
    if len(terms) <= 1:
        # We require at least two terms for a ratio.
        return
    factor = 1.0
    matched = []
    unmatched = terms.copy()
    for target in terms:
        if target not in matched:
            if match := _match_terms(target, unmatched):
                value, term = match
                if term != target:
                    for this in (target, term):
                        matched.append(this)
                        unmatched.remove(this)
                else:
                    matched.append(target)
                    unmatched.remove(target)
                factor *= value
    if not unmatched:
        return factor


def _match_terms(
    target: symbolic.Term,
    terms: typing.Iterable[symbolic.Term],
) -> typing.Optional[typing.Union[float, symbolic.Term]]:
    """Attempt to convert `target` to a term in `terms`."""
    u0 = target.base
    exponent = target.exponent
    like_terms = [
        term for term in terms
        if term != target and term.exponent == -exponent
    ]
    for term in like_terms:
        u1 = term.base
        if conversion := _convert_as_strings(u0, u1):
            return conversion ** exponent, term
    dimensions = _defined.NamedUnit(u0).dimensions.values()
    if u0 in _reference.NAMED_UNITS and all(d == '1' for d in dimensions):
        return 1.0, target


@etc.autostr
class Converter:
    """Unit-conversion handler for a known physical quantity."""

    def __init__(
        self,
        unit: str,
        quantity: str,
        substitutions: typing.Dict[str, str],
    ) -> None:
        self._unit = substitutions.get(unit) or unit
        self._quantity = quantity
        self._substitutions = substitutions

    def to(self, target: str):
        """Compute the conversion from the current unit to `target`.
        
        Parameters
        ----------
        target : string
            The unit or metric system to which to convert the current unit.

        Returns
        -------
        `~Conversion`

        Notes
        -----
        This method proceeds as follows:
        
        1. Substitute the appropriate unit if `target` is a metric system.
        1. Immediately return a trivial conversion object (i.e., with a `factor`
           of 1.0) if the target unit and the current unit are equal.
        1. Attempt a brute-force conversion via the `~factory` function and, if
           successful, return the resulting conversion object.
        1. Raise an exception to alert the caller that the conversion is
           undefined.
        """
        unit = self._substitutions.get(target) or target
        if self.unit == unit:
            return Conversion(self.unit, unit)
        if result := conversion_factory(self.unit, unit):
            return result
        raise ValueError(
            f"Unknown conversion from {self.unit!r} to {unit!r}."
        ) from None

    def __str__(self) -> str:
        return f"{self.unit!r} [{self.quantity!r}]"

    @property
    def unit(self):
        """The unit from which to convert."""
        return self._unit

    @property
    def quantity(self):
        """The physical quantity of `unit`."""
        return self._quantity


_converters = {}
"""Internal collection of unit-conversion handlers.

This module-level collection is a mapping from unit-quantity pairs to their
correpsonding `~Converter` instances. It exists to preclude the existence of
redundant unit-conversion handlers.
"""

def converter_factory(unit: str, quantity: str) -> Converter:
    """Create a new unit-conversion handler.

    Parameters
    ----------
    unit : string
        The unit to be converted.

    quantity : string
        The physical quantity of `unit`.

    Returns
    -------
    `~Converter`
        The unit-conversion handler corresponding to `unit` and `quantity`.

    Raises
    ------
    `ValueError`
        The given quantity is not a known physical quantity.
    """
    if available := _converters.get((unit, quantity)):
        return available
    substitutions = _get_substitutions(quantity)
    c = Converter(unit, quantity, substitutions)
    _converters[(unit, quantity)] = c
    return c


def _get_substitutions(quantity: str):
    """Get appropriate metric-system unit substitutions for `~converter`.
    
    This function exists to handle edge cases, such as treating atomic mass
    number quantities as mass quantities when converting to the equivalent unit
    in a given metric system.
    
    As a specific example, suppose you have a mass-like quantity with unit
    'nuc'. Since the metric quantity of 'nuc' is 'mass number', not 'mass', the
    default unit substitution would be '1' for both 'mks' and 'cgs'. However,
    intuition suggests that converting a mass-like quantity to 'mks' or 'cgs'
    should produce a quantity with unit 'kg' or 'g', respectively. This function
    therefore handles the special case of 'mass number' by replacing the default
    substitutions with the substitutions for 'mass'.
    """
    if quantity.lower() in {'mass number', 'mass_number'}:
        return _defined.UNITS['mass']
    try:
        substitutions = _defined.UNITS[quantity]
    except KeyError as err:
        raise ValueError(
            f"Unknown quantity {quantity!r}"
        ) from err
    return substitutions


def convert(source: str, target: str, quantity: str=None):
    """Convert `source` to `target`."""
    if not isinstance(source, str):
        raise TypeError(
            f"Argument to source must be a string, not {type(source)}"
        ) from None
    if not isinstance(target, str):
        raise TypeError(
            f"Argument to target must be a string, not {type(target)}"
        ) from None
    if target in _reference.SYSTEMS:
        if source == '1':
            return conversion_factory(source, '1')
        if quantity is None:
            if _is_ambiguous(source, target):
                raise _exceptions.UnitConversionError(
                    f"Conversion from {source!r} to {target!r}"
                    " is ambiguous without knowledge of physical quantity"
                ) from None
            q = _defined.get_quantity(symbolic.expression(source))
            return converter_factory(source, quantity=str(q)).to(target)
        return converter_factory(source, quantity=quantity).to(target)
    return conversion_factory(source, target)


def _is_ambiguous(unit: str, system: str):
    """True if the conversion from `unit` to `system` is ambiguous.

    Notes
    -----
    - This function is an internal helper for `~convert`.
    - This function will return `False` if either there is exactly one defined
      conversion from `unit` in `system`, or `unit` is not a canonical unit in
      `system`. The latter case does not guarantee a successful conversion; it
      simply allows this function to exit early if it has no chance of
      identifying an ambiguous conversion.
    """
    units = _defined.EQUIVALENT['units']
    others = {s for s in _reference.SYSTEMS if s != system}
    expr = symbolic.expression(unit)
    for s in others:
        targets = {v[system] for v in units.values() if v[s] == expr}
        if len(targets) > 1:
            return True
    return False

