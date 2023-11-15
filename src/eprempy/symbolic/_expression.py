import collections
import collections.abc
import fractions
import functools
import numbers
from operator import attrgetter
import typing

from .. import etc
from . import _operand
from . import _parser


S = typing.TypeVar('S', str, numbers.Number)


class Expression(collections.abc.Sequence):
    """An object representing a symbolic expression."""

    def __init__(self, terms: typing.List[_operand.Term]) -> None:
        self._terms = terms

    def __bool__(self) -> bool:
        """True if this expression is not empty."""
        return not self.isempty

    @property
    def isempty(self):
        """True if this expression contains no terms."""
        return not self.terms

    def __iter__(self) -> typing.Iterator[_operand.Term]:
        return iter(self.terms)

    def __len__(self) -> int:
        return len(self.terms)

    @typing.overload
    def __getitem__(self, index: typing.SupportsIndex) -> _operand.Term: ...

    @typing.overload
    def __getitem__(self, index: slice) -> typing.Iterable[_operand.Term]: ...

    def __getitem__(self, index):
        """Access terms via standard indexing."""
        if isinstance(index, typing.SupportsIndex):
            idx = int(index)
            if idx > len(self):
                raise IndexError(index)
            if idx < 0:
                idx += len(self)
            return self.terms[idx]
        if isinstance(index, slice):
            return self.terms[index]
        raise IndexError(
            f"Invalid index for expression: {index}"
        ) from None

    def __str__(self) -> str:
        """A simplified representation of this instance."""
        return self.format()

    def __repr__(self):
        """An unambiguous representation of this object."""
        return f"{self.__class__.__qualname__}({self})"

    def format(self, style: str=None, *, separator: str=' '):
        """Join symbolic terms into a string.

        Parameters
        ----------
        style : string, optional
            The style in which to format each term. See `~Operand.format` for
            available styles.

        separator : string, default=' '
            The string to place between terms.
        """
        formatted = (term.format(style=style) for term in self)
        return separator.join(formatted)

    def difference(self, other, symmetric: bool=False, split: bool=False):
        """Compute the difference between two expressions.
        
        Parameters
        ----------
        other
            The object with respect to which to compute the difference. If
            `other` is not a `~symbolic.Expression`, this method will convert it
            to one before proceeding.

        symmetric : bool, default=False
            If true, compute the symmetric difference between this expression
            and `other`.

        split : bool, default=False
            If true, return the one-sided differences in a `list`. The first
            element contains the terms in this expression that are not in
            `other`, and the second element contains the terms in `other` that
            are not in this expression.

        Notes
        -----
        The `split` keyword argument takes precedence over the `symmetric`
        keyword argument because the result of the former contains more
        imformation than the result of the latter. See Examples for a suggestion
        on converting a split result into a symmetric result.

        Examples
        --------
        Consider the following two expressions:
        
        >>> e0 = symbolic.expression('a * b')
        >>> e1 = symbolic.expression('a * c')

        Their formal (one-sided) difference is

        >>> e0.difference(e1)
        {symbolic.term(b)}

        Their formal symmetric difference is

        >>> e0.difference(e1, symmetric=True)
        {symbolic.term(b), symbolic.term(c)}

        Passing `split=True` produces a `list` of `set`s

        >>> e0.difference(e1, split=True)
        [{symbolic.term(b)}, {symbolic.term(c)}]

        To convert a split result into a symmetric result, simply compute the
        union of the former:

        >>> symmetric = e0.difference(e1, symmetric=True)
        >>> split = e0.difference(e1, split=True)
        >>> set.union(*split) == symmetric
        True
        """
        if not isinstance(other, Expression):
            other = expression_factory(other)
        s0 = set(self.terms)
        s1 = set(other.terms)
        if split:
            return [s0 - s1, s1 - s0]
        if symmetric:
            return s0 ^ s1
        return s0 - s1

    def __hash__(self):
        """Compute hash(self)."""
        return hash(tuple(self.terms))

    @property
    def terms(self):
        """The symbolic terms in this expression."""
        return self._terms

    def __eq__(self, other) -> bool:
        """True if two expressions have the same symbolic terms.

        This method defines two expressions as equal if they have equivalent
        lists of symbolic terms (a.k.a simple parts), regardless of order, after
        parsing. Two expressions with different numbers of terms are always
        false. If the expressions have the same number of terms, this method
        will sort the triples (first by base, then by exponent, and finally by
        coefficient) and compare the sorted lists. Two expressions are equal if
        and only if their sorted lists of terms are equal.

        If `other` is not an instance of this class, this method will first
        attempt to convert it.
        """
        if not isinstance(other, Expression):
            other = expression_factory(other)
        if len(self) != len(other):
            return False
        key = attrgetter('base', 'exponent', 'coefficient')
        return sorted(self, key=key) == sorted(other, key=key)

    def __mul__(self, other):
        """Called for self * other.

        This method implements multiplication between two expressions by
        reducing the exponents of terms with a common base. If `other` is a
        string, it will first attempt to convert it to an `Expression`.
        """
        that = other if isinstance(other, Expression) else expression_factory(other)
        if not that:
            return NotImplemented
        reduced = reduce(self, that)
        return expression_factory(reduced)

    def __rmul__(self, other: typing.Any):
        """Called for other * self."""
        return expression_factory(other).__mul__(self)

    def __truediv__(self, other):
        """Called for self / other.

        This method implements division between two expressions by raising all
        terms in `other` to -1, then reducing the exponents of terms with a
        common base. If `other` is a string, it will first attempt to convert it
        to an `Expression`.
        """
        that = other if isinstance(other, Expression) else expression_factory(other)
        if not that:
            return NotImplemented
        return expression_factory(reduce(self, [term ** -1 for term in that]))

    def __rtruediv__(self, other: typing.Any):
        """Called for other / self."""
        return expression_factory(other).__truediv__(self)

    def __pow__(self, exp: numbers.Real):
        """Called for self ** exp.

        This method implements exponentiation of an expression by raising all
        terms to the given power, then reducing exponents of terms with a common
        base. It will first attempt to convert `exp` to a float.
        """
        exp = float(exp)
        if not exp:
            return NotImplemented
        terms = [pow(term, exp) for term in self]
        return expression_factory(reduce(terms))

    def apply(self, update: typing.Callable):
        """Create a new expression by applying the given callable object.
        
        Parameters
        ----------
        update : callable
            The callable object that this method should use to update the base
            of each term in this expression.

        Returns
        -------
        `~symbolic.Expression`
        """
        bases = [update(term.base) for term in self]
        exponents = [term.exponent for term in self]
        result = bases[0] ** exponents[0]
        for base, exponent in zip(bases[1:], exponents[1:]):
            result *= base ** exponent
        return result


@typing.overload
def expression_factory(*args, **kwargs) -> Expression:
    """Create an expression from the given arguments, if possible."""

@typing.overload
def expression_factory(expression: S, /, **kwargs) -> Expression:
    """Create an expression from a single value.

    Parameters
    ----------
    expression : string or number
        The value to convert into an expression.

    **kwargs
        Keywords to pass to `~symbolic.Parser`.

    Examples
    --------
    Create a symbolic expression from a string that represents the result of
    multiplying `a^3/2` by `b`, dividing by `c^1/2`, and squaring the ratio:

    >>> symbolic.expression('(a^3/2 * b / c^1/2)^2')
    symbolic.Expression(a^3 b^2 c^-1)
    """

@typing.overload
def expression_factory(
    expression: typing.Iterable[S],
    /,
    **kwargs,
) -> Expression:
    """Create an expression from an iterable of values.

    Parameters
    ----------
    expression : iterable of strings or numbers
        The iterable object with which to initialize the new instance. All
        members must support conversion to a string in the form of a
        `~symbolic.Term`.

    **kwargs
        Keywords to pass to `~symbolic.Parser`.

    Examples
    --------
    Create a symbolic expression from a list of the individual string terms in
    the result of multiplying `a^3/2` by `b`, dividing by `c^1/2`, and squaring
    the ratio:

    >>> symbolic.expression(['a^3', 'b', 'c^-1'])
    symbolic.Expression(a^3 b c^-1)
    """

@typing.overload
def expression_factory(expression: Expression, /) -> Expression:
    """Create an expression from an expression.

    This mode exists to support algorithms that don't know the type of argument
    until runtime. If the type is known, it is simpler to use the existing
    instance.

    Parameters
    ----------
    expression : `~symbolic.Expression`
        An existing instance of this class.

    Examples
    --------
    Create an instance from a string:

    >>> this = symbolic.expression('a * b / c')

    Pass the first instance to this class:

    >>> that = symbolic.expression(this)

    Both `this` and `that` represent the same expression...

    >>> this
    symbolic.expression(a b c^-1)
    >>> that
    symbolic.expression(a b c^-1)

    ...because they are the same object.

    >>> that is this
    True
    """

def expression_factory(this, **options):
    if isinstance(this, Expression):
        if not options:
            return this
        raise ValueError(
            f"Cannot update parsing options on an existing expression"
        ) from None
    string = standard(this, joiner='*')
    terms = _init_terms(string, _parser.Parser(**options))
    return Expression(terms)


def standard(
    this,
    missing: typing.Optional[str]=None,
    joiner: str='*',
) -> str:
    """Convert `this` to a standard format.
    
    Parameters
    ----------
    this : string or iterable
        The object to convert.

    missing : string, optional
        The value to return if `this` is null.

    joiner : string, default='*'
        The string token to use when joining parts of an iterable argument.

    See Also
    --------
    `~symbolic.Expression`: A class that represents one or more terms joined by
    symbolic operators and grouped by separator characters. Instances support
    multiplication and division with strings or other instances, and
    exponentiation by real numbers. Instantiation automatically calls this
    function.
    """
    if etc.isnull(this):
        return missing
    if isinstance(this, str):
        return this
    try:
        iter(this)
    except TypeError:
        return str(this)
    else:
        return joiner.join(f"({part})" for part in this)


def _init_terms(
    string: str,
    parser: _parser.Parser,
) -> typing.List[_operand.Term]:
    """Initialize terms for an expression by parsing `string`."""
    if string is None:
        return []
    terms = parser.parse(string)
    return reduce(terms)


def reduce(*groups: typing.Iterable[_operand.Term]):
    """Algebraically reduce terms with equal bases.

    Parameters
    ----------
    *groups : tuple of iterables
        One or more iterables of `~symbolic.Term` instances. If there are
        multiple groups, this method will combine all terms it finds in the full
        collection of groups.

    Notes
    -----
    This function will sort terms in order of ascending exponent, and
    alphabetically for equal exponents.
    """
    terms = [t for group in groups for t in group]
    reduced = {}
    for t in terms:
        if t.base in reduced:
            reduced[t.base]['coefficient'] *= t.coefficient
            reduced[t.base]['exponent'] += t.exponent
        else:
            attributes = {
                'coefficient': t.coefficient,
                'exponent': t.exponent,
            }
            reduced[t.base] = attributes
    fracs = [
        fractions.Fraction(v['coefficient'])
        for v in reduced.values()
    ]
    tmp = [
        _operand.term_factory(base=k, exponent=v['exponent'])
        for k, v in reduced.items()
        if k != '1' and v['exponent'] != 0
    ]
    # Sort: high to low in exponent, followed by alphabetic in base.
    variables = sorted(
        sorted(tmp, key=attrgetter('base')),
        key=attrgetter('exponent'),
        reverse=True,
    )
    c = functools.reduce(lambda x, y: x*y, fracs)
    constant = [_operand.term_factory(coefficient=c)]
    if not variables:
        return constant
    if c == 1:
        return variables
    return constant + variables


