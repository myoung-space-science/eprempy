import fractions
import itertools
import numbers
import re
import typing

from .. import etc
from . import _part


class OperandTypeError(TypeError):
    """Type error associated with a symbolic operand."""


class OperandValueError(ValueError):
    """Value error associated with a symbolic operand."""


@etc.autostr
class Operand(_part.Part):
    """An operand in a symbolic expression.

    Algebraic operands mainly exist to support the `~symbolic.Expression` class.
    They may be simple or general, as described below.

    A simple symbolic operand has the form [c]b[^e] or c[^e], where `c` is a
    numerical coefficient, `b` is a string base, and `e` is a numerical
    exponent. Braces ('[]') denote an optional component that defaults to a
    value of 1. The `~symbolic.Term` class formally represents simple symbolic
    operands; the form [c]b[^e] corresponds to a variable term and the form
    c[^e] corresponds to a constant term.

    Examples include:
    
    * `'1'`: unity / multiplicative identity
    * `'1^n'` (`n` real): constant equivalent to unity
    * `'m^n'` (`m`, `n` real): arbitrary constant
    * `'V'`: variable 'V' with coefficient 1 and exponent 1
    * `'V^n'` (`n` real): variable 'V' with coefficient 1 and exponent n
    * `'mV'` (`m` real): variable 'V' with coefficient m and exponent 1
    * `'mV^n'` (`m`, `n` real): variable 'V' with coefficient m and exponent n

    Note that the base of a variable term may comprise multiple characters as
    long as it does not begin with a digit, which this class will interpret as
    part of the coefficient.

    A general symbolic operand consists of simpler operands (though not
    necessarily formally simple operands) combined with symbolic operators and
    separators. All formally simple operands are general operands. The following
    are examples of (non-simple) general symbolic operands:

    * `'a * b^2'` <=> `'(a * b^2)'` <=> `'(a * b^2)^1'`
    * `'(a * b^2)^3'`
    * `'(a * b^2)^3/2'`
    * `'((a / b^2)^3 * c)^2'`
    * `'(a / b^2)^3 * c^2'`
    * `'a / (2 * 4b)'`
    * `'(2a * b)^3 / (4 * c)'`

    There are many more ways to construct a general operand than a simple
    operand. This is by design, to support building instances of
    `~symbolic.Expression` with `~symbolic.Parser`.
    """

    def __init__(
        self,
        coefficient: numbers.Real=None,
        base: str=None,
        exponent: numbers.Real=None,
    ) -> None:
        self.coefficient = fractions.Fraction(coefficient or 1)
        """The numerical coefficient."""
        self.base = base or '1'
        """The base term or complex."""
        self.exponent = fractions.Fraction(exponent or 1)
        """The numerical exponent."""

    @property
    def attrs(self):
        """The current coefficient, base, and exponent."""
        return (self.coefficient, self.base, self.exponent)

    def __pow__(self, power):
        """Create a new operand, raised to `power`."""
        coefficient = self.coefficient ** power
        exponent = self.exponent * power
        return type(self)(coefficient, self.base, exponent)

    def __mul__(self, other):
        """Create a new operand, multiplied by `other`."""
        coefficient = self.coefficient * other
        return type(self)(coefficient, self.base, self.exponent)

    __rmul__ = __mul__

    def __eq__(self, other) -> bool:
        """True if two operands' attributes are equal."""
        if not isinstance(other, Operand):
            return NotImplemented
        if not other.base == self.base:
            return False
        return all(
            float(getattr(other, attr)) == float(getattr(self, attr))
            for attr in ('exponent', 'coefficient')
        )

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return self.format()

    def format(self):
        """Format this operand for printing."""
        if self.coefficient == 1 and self.exponent == 1:
            return self.base
        string = f"({self.base})"
        if self.exponent != 1:
            string = f"{string}^{self.exponent}"
        if self.coefficient != 1:
            string = f"{self.coefficient}{string}"
        return string


class OperandFactory(_part.Factory):
    """A factory that produces symbolic operands."""

    rational = r""" # Modeled after `fractions._RATIONAL_FORMAT`
        [-+]?                 # an optional sign, ...
        (?=\d|\.\d)           # ... only if followed by <digit> or .<digit>
        \d*                   # and a possibly empty numerator
        (?:                   # followed by ...
            (?:/\d+?)         # ... an optional denominator
        |                     # OR
            (?:\.\d*)?        # ... an optional fractional part,
            (?:[eE][-+]?\d+)? #     and an optional exponent
        )
    """
    base = r"""
        [a-zA-Z#_]+ # one or more accepted non-digit character(s)
        \d*         # followed by optional digits
    """

    def __init__(
        self,
        opening: str='(',
        closing: str=')',
        raising: str='^',
    ) -> None:
        exponent = fr'\{raising}{self.rational}'
        self.patterns = {
            'constant': re.compile(
                fr'(?P<coefficient>{self.rational})'
                fr'(?P<exponent>{exponent})?',
                re.VERBOSE,
            ),
            'variable': re.compile(
                fr'(?P<coefficient>{self.rational})?'
                fr'(?P<base>{self.base})'
                fr'(?P<exponent>{exponent})?',
                re.VERBOSE,
            ),
            'complex': re.compile(
                fr'(?P<coefficient>{self.rational})?'
                fr'(?P<base>\{opening}.+?\{closing})'
                fr'(?P<exponent>{exponent})?',
                re.VERBOSE,
            ),
            'exponent': re.compile(exponent, re.VERBOSE),
            'opening': re.compile(fr'\{opening}', re.VERBOSE),
            'closing': re.compile(fr'\{closing}', re.VERBOSE),
            'raising': re.compile(fr'\{raising}', re.VERBOSE)
        }
        """Compiled regular expressions for symbolic operands."""

    _argtypes = {
        'coefficient': numbers.Real,
        'base': str,
        'exponent': (numbers.Real, str),
    }
    @classmethod
    def isvalid(cls, name: str, this: typing.Any):
        """True if `this` is valid for use as the named attribute."""
        return isinstance(this, cls._argtypes[name])

    def normalize(self, *args):
        """Extract attributes from the given argument(s)."""
        try:
            nargs = len(args)
        except TypeError:
            raise OperandTypeError(args) from None
        if nargs == 1:
            return self._length_1(args)
        if nargs == 2:
            return self._length_2(args)
        if nargs == 3:
            return self._length_3(args)
        raise OperandValueError(
            f"{self.__class__.__qualname__}"
            f" accepts 1, 2, or 3 arguments"
            f" (got {nargs})"
        )

    def _length_1(self, args: typing.Any):
        """Normalize a length-1 argument tuple, if possible.

        A length-1 tuple may represent either:

        - coefficient <Real>
        - base <str>

        If it has one of these forms, this method will substitute the default
        value for the missing attributes; otherwise, it will raise an exception.
        """
        arg = args[0]
        names = ('base', 'coefficient')
        for name in names:
            given = {name: arg}
            if self.isvalid(name, arg):
                return self.standardize(fill=True, **given)
        raise OperandTypeError(
            "A single argument may be either"
            " a coefficient <Real> or a base <str>;"
            f" not {type(arg)}"
        )

    def _length_2(self, args: typing.Any):
        """Normalize a length-2 argument tuple, if possible.

        A length-2 tuple may represent either:

        - (base <str>, exponent <Real or str>)
        - (coefficient <Real>, exponent <Real or str>)
        - (coefficient <Real>, base <str>)

        If it has one of these forms, this method will substitute the default
        value for the missing attribute; otherwise, it will raise an exception.
        """
        combinations = itertools.combinations(self._argtypes, 2)
        for names in combinations:
            given = dict(zip(names, args))
            if all(self.isvalid(name, arg) for name, arg in given.items()):
                return self.standardize(fill=True, **given)
        badtypes = [type(arg) for arg in args]
        raise OperandTypeError(
            "Acceptable two-argument forms are"
            " (base <str>, exponent <Real or str>),"
            " (coefficient <Real>, exponent <Real or str>),"
            " or"
            " (coefficient <Real>, base <str>);"
            " not"
            f"({', '.join(str(t) for t in badtypes)})"
        )

    def _length_3(self, args: typing.Any):
        """Normalize a length-3 argument tuple.

        A length-3 tuple must have the form (coefficient <Real>, base <str>,
        exponent <Real or str>).
        """
        return self.standardize(
            coefficient=args[0],
            base=args[1],
            exponent=args[2],
            fill=True,
        )

    def create(self, *args, strict: bool=False) -> typing.Optional[Operand]:
        """Create an operand from input.

        Parameters
        ----------
        *args
            The object(s) from which to create an operand, if possible. This may
            take one of the following forms: a single string representing the
            base operand; a numerical coefficient and a base string; a base
            string and a numerical exponent; or a coefficient, base, and
            exponent. A missing coefficient or exponent will default to 1.

        strict : bool, default=false
            If true, this method will return `None` if it is unable to create an
            operand from `*args`. The default behavior is to return the input
            (with default coefficient and exponent, if necessary) as an instance
            of `~symbolic.Operand`.

        Returns
        -------
        `~symbolic.Operand` or `None`
            An instance of `~symbolic.Operand` or one of its subclasses if the
            input arguments represent a valid operand. The `strict` keyword
            dictates the return behavior when input does not produce an operand.

        Notes
        -----
        This method will create the most general symbolic operand possible from
        the initial string. It will parse a simple symbolic operand into a
        coefficient, variable, and exponent but it will not attempt to fully
        parse a general symbolic operand into simpler operands (i.e. symbolic
        terms). In other words, it will do as little work as possible to extract
        a coefficient and exponent, and the expression on which they operate. If
        all attempts to determine appropriate attributes fail, the value of
        `strict` controls its return behavior.
        
        See note at `parse` for differences between this method and that.

        The following examples use the general symbolic operands described in
        `~symbolic.Operand` to illustrate the minimal parsing described above:

        - `'a * b^2'` <=> `'(a * b^2)'` <=> `'(a * b^2)^1'` -> `1, 'a * b^2', 1`
        - `'2a * b^2'` -> `1, '2a * b^2', 1`
        - `'2(a * b^2)'` -> `2, 'a * b^2', 1`
        - `'(a * b^2)^3'` -> `1, 'a * b^2', 3`
        - `'2(a * b^2)^3'` -> `2, 'a * b^2', 3`
        - `'(a * b^2)^3/2'` -> `1, 'a * b^2', '3/2'`
        - `'((a / b^2)^3 * c)^2'` -> `1, '(a / b^2)^3 * c', 2`
        - `'(a / b^2)^3 * c^2'` -> `1, '(a / b^2)^3 * c^2', 1`
        """
        c0, b0, e0 = self.normalize(*args).values()
        ends = (b0[0], b0[-1])
        if any(self.patterns['raising'].match(c) for c in ends):
            raise OperandValueError(b0) from None
        match = self.search(b0, mode='fullmatch')
        if not match:
            if not strict:
                return Operand(c0, b0, e0)
            return
        if not isinstance(match.result, Operand):
            raise TypeError(
                f"Expected Operand but got {type(match.result)}"
            ) from None
        c1, base, e1 = match.result.attrs
        coefficient = c0 * (c1 ** e0)
        exponent = e1 * e0
        if not isinstance(match.result, Term):
            interior = self.create(base)
            if isinstance(interior, Term):
                coefficient *= interior.coefficient ** exponent
                base = interior.base
                exponent *= interior.exponent
                return term_factory(
                    coefficient=coefficient,
                    base=base,
                    exponent=exponent,
                )
            return Operand(
                coefficient=coefficient,
                base=base,
                exponent=exponent,
            )
        return term_factory(
            coefficient=coefficient,
            base=base,
            exponent=exponent,
        )

    def parse(self, string: str):
        """Extract an operand at the start of `string`, possible.
        
        Notes
        -----
        The primary difference between `~create` and `~parse` is as follows:

        - `~create` resolves input into (coefficient, base, exponent), then
          creates an appropriate operand from the base string, then applies the
          input coefficient and exponent, and finally returns the operand.

        - `~parse` attempts to match an operand at the start of a string, then
          creates an appropriate operand from only that substring, and finally
          returns the operand and the remainder of the string.
        """
        stripped = string.strip()
        if match := self.search(stripped):
            return match

    def search(self, string: str, **kwargs):
        """Search for an operand in the given string.
        
        Parameters
        ----------
        string
            The string to which to apply pattern-matching methods in an attempt
            to find an appropriate operand.

        **kwargs
            Keyword arguments to pass to the pattern-matching methods.

        Returns
        -------
        `~symbolic.PartMatch` or `None`
            An object representing the matched substring and contextual
            information, if any attemp to match was successful. If no method
            found an operand in `string` (subject to any given keyword
            arguments), this method will return `None`.
        """
        methods = (
            self._match_simplex,
            self._match_complex,
        )
        if match := etc.apply(methods, string, **kwargs):
            return match

    def _match_simplex(
        self,
        string: str,
        mode: str='match',
        start: int=0,
    ) -> typing.Optional[_part.Match[Operand]]:
        """Attempt to find an irreducible term at the start of `string`.

        Notes
        -----
        This method tries to match the 'variable' pattern before the 'constant'
        pattern because `re.match` will find a match for 'constant' at the start
        of any variable term with an explicit coefficient.
        """
        target = string[start:]
        matches = {
            key: self._get_match_method(key, mode)(target)
            for key in ('variable', 'constant')
        }
        if not any(matches.values()):
            return
        if all(matches.values()):
            same = matches['variable'][0] == matches['constant'][0]
            key = 'constant' if same else 'variable'
            build_method = self._get_build_method(key)
            return build_method(matches[key])
        for key, match in matches.items():
            if match:
                return self._get_build_method(key)(match)

    def _get_match_method(
        self,
        pattern: str,
        mode: str,
    ) -> typing.Callable[[str], re.Match]:
        """Look up the appropriate matching method for `pattern` and `mode`."""
        return getattr(self.patterns[pattern], mode)

    def _get_build_method(
        self,
        pattern: str,
    ) -> typing.Callable[[re.Match], _part.Match[Operand]]:
        """Look up the appropriate building method for `pattern`."""
        return getattr(self, f'_build_{pattern}')

    def _build_variable(self, match: re.Match):
        """Build a variable term from a match object."""
        standard = self.standardize(**match.groupdict(), fill=True)
        return _part.Match(
            result=term_factory(**standard),
            context=match,
        )

    def _build_constant(self, match: re.Match):
        """Build a constant term from a match object."""
        standard = self.standardize(**match.groupdict(), fill=True)
        coefficient = standard['coefficient'] ** standard['exponent']
        return _part.Match(
            result=term_factory(coefficient=float(coefficient)),
            context=match,
        )

    def _match_complex(
        self,
        string: str,
        mode: str='match',
        start: int=0,
    ) -> typing.Optional[_part.Match[Operand]]:
        """Attempt to match a complex operand at the start of `string`."""
        target = string[start:]
        bounds = self.find_bounds(target)
        if not bounds:
            return
        i0, end = bounds
        result = {'base': target[i0+1:end-1]}
        if match := self._match_simplex(target[:i0], mode='fullmatch'):
            result['coefficient'] = match.result.coefficient
            i0 = 0
        if mode == 'match' and i0 != 0:
            return
        if exp := self.patterns['exponent'].match(target[end:]):
            result['exponent'] = exp[0]
            end += exp.end()
        if mode == 'fullmatch' and (i0, end) != (0, len(target)):
            return
        standard = self.standardize(**result, fill=True)
        return _part.Match(
            result=Operand(**standard),
            context={'end': end, 'start': start, 'string': string},
        )

    def find_bounds(self, string: str):
        """Find the indices of the first bounded substring, if any.
        
        A bounded substring is any portion of `string` that is bounded on the
        left by the opening separator and on the right by the closing separator.
        Opening and closing separators are an immutable attribute of an instance
        of this class.

        Parameters
        ----------
        string
            The string in which to search for a bounded substring.

        Returns
        -------
        tuple of int, or `None`
            The index of the leftmost opening separator and the index of the
            first character beyond the rightmost closing separator (possibly the
            end), if there is a bounded substring; otherwise, `None`. The
            convention is such that if `start, end = find_bounds(string)`,
            `string[start:end]` will produce the bounded substring with bounds.

        Examples
        --------
        Define a list of test strings::

            >>> strings = [
            ...     '(a*b)',
            ...     '(a*b)^2',
            ...     '3(a*b)',
            ...     '3(a*b)^2',
            ...     '3(a*b)^2 * (c*d)',
            ...     '4a^4',
            ...     '3(4a^4)^3',
            ...     '2(3(4a^4)^3)^2',
            ... ]

        Create an instance of this class with the default operators and
        separators::

            >>> operand = symbolic.OperandFactory()

        Find the bounding indices of each test string, if any, and display the
        corresponding substring::

            >>> for string in strings:
            ...     bounds = operand.find_bounds(string)
            ...     print(f"{bounds}: {string!r} -> ", end='')
            ...     if bounds:
            ...         start, end = bounds
            ...         result = f"{string[start:end]}"
            ...     else:
            ...         result = string
            ...     print(f"{result!r}")
            ... 
            (0, 5): '(a*b)' -> '(a*b)'
            (0, 5): '(a*b)^2' -> '(a*b)'
            (1, 6): '3(a*b)' -> '(a*b)'
            (1, 6): '3(a*b)^2' -> '(a*b)'
            (1, 6): '3(a*b)^2 * (c*d)' -> '(a*b)'
            None: '4a^4' -> '4a^4'
            (1, 7): '3(4a^4)^3' -> '(4a^4)'
            (1, 12): '2(3(4a^4)^3)^2' -> '(3(4a^4)^3)'
        """
        initialized = False
        count = 0
        i0 = 0
        for i, c in enumerate(string):
            if self.patterns['opening'].match(c):
                count += 1
                if not initialized:
                    i0 = i
                    initialized = True
            elif self.patterns['closing'].match(c):
                count -= 1
            if initialized and count == 0:
                return i0, i+1

    def standardize(
        self,
        fill: bool=False,
        **given
    ) -> typing.Dict[str, typing.Union[float, int, str, fractions.Fraction]]:
        """Cast to appropriate types and fill in defaults, if necessary."""
        full = {
            'coefficient': {'callable': self._standard_coefficient},
            'base': {'callable': self._standard_base},
            'exponent': {'callable': self._standard_exponent},
        }
        default = self.fill_defaults(**dict.fromkeys(full.keys()))
        updatable = full.copy() if fill else {k: full[k] for k in given}
        return {
            key: attr['callable'](given.get(key) or default[key])
            for key, attr in updatable.items()
        }

    def _standard_coefficient(self, v):
        """Convert input to a standard coefficient."""
        return fractions.Fraction(v or 1)

    def _standard_base(self, v):
        """Convert input to a standard base."""
        return str(v)

    def _standard_exponent(self, v):
        """Convert input to a standard exponent."""
        if isinstance(v, str):
            v = self.patterns['raising'].sub('', v)
        return fractions.Fraction(v or 1)

    def fill_defaults(self, **given):
        """Return the default value for any explicitly null arguments.

        If the given key-value pairs contain an argument with a null value
        (e.g., `None`), this method will replace it with the default value. It
        will pass all other values through unaltered and will not fill in
        default values corresponding to other keys.
        """
        defaults = {
            'coefficient': 1,
            'base': '1',
            'exponent': 1,
        }
        given.update(
            {
                key: defaults[key]
                for key, value in given.items()
                if key in defaults and not value
            }
        )
        return given

    def strip_separators(self, string: str):
        """Remove one opening and one closing separator."""
        opened = self.patterns['opening'].match(string[0])
        closed = self.patterns['closing'].match(string[-1])
        if not (opened and closed):
            return string
        string = self.patterns['opening'].sub('', string, count=1)
        string = self.patterns['closing'].sub('', string[::-1], count=1)
        return string[::-1]


class Term(Operand):
    """A symbolic operand with an irreducible base.
    
    In the single-argument form, the user provides only the base quantity by
    positional-only argument. In the triple-argument form, the user provides the
    coefficient, base, and exponent by positional or keyword argument(s), with
    the caveat that if one argument is positional, they must all be positional.
    This restriction prevents ambiguity among the possible double-argument
    combinations.
    """

    # NOTE: Currently redundant with `OperandFactory`.

    rational = r""" # Modeled after `fractions._RATIONAL_FORMAT`
        [-+]?                 # an optional sign, ...
        (?=\d|\.\d)           # ... only if followed by <digit> or .<digit>
        \d*                   # and a possibly empty numerator
        (?:                   # followed by ...
            (?:/\d+?)         # ... an optional denominator
        |                     # OR
            (?:\.\d*)?        # ... an optional fractional part,
            (?:[eE][-+]?\d+)? #     and an optional exponent
        )
    """
    base = r"""
        [a-zA-Z#_]+ # one or more accepted non-digit character(s)
        \d*         # followed by optional digits
    """
    _base_re = re.compile(fr'({rational}|{base})', re.VERBOSE)

    @classmethod
    def base_is_valid(cls, base):
        """True if `base` can initialize a symbolic term."""
        return bool(cls._base_re.fullmatch(str(base)))

    def __call__(self, value: numbers.Real):
        """Evaluate a variable term at this value.
        
        This method will attempt to substitute `value` for this term's `base`
        attribute. If successful, it will return a constant term that the caller
        may cast to `int` or `float` type.

        Parameters
        ----------
        value : real
            The numerical value at which to evaluate this term.

        Returns
        -------
        `~symbolic.Term`
            A new instance of this class equivalent to the constant numerical
            value of this term when `base == value`.
        """
        if not isinstance(value, numbers.Real):
            errmsg = f"Can't evaluate term with value {value!r}"
            raise TypeError(errmsg)
        if self.base != '1':
            coefficient = self.coefficient * (value ** self.exponent)
            return type(self)(coefficient=coefficient)
        errmsg = f"Can't evaluate term with base {self.base!r}"
        raise TypeError(errmsg)

    def format(self, style: str=None):
        """Format this term.

        Parameters
        ----------
        style : string, optional
            Select a the formatting style. The default behavior is to represent
            this term in the form `'cb^e'`, where `c` is the coefficient, `b` is
            the base, and `e` is the exponent. See Styles for supported styles.

        Styles
        ------
        This section lists the supported formatting styles. All strings are
        case-insensitive unless otherwise noted.
        
        - `'tex'`: format the term for TeX-like display.
        """
        coefficient = self._format_coefficient()
        if self.base == '1':
            return f"{coefficient}"
        fmt = style or ''
        exponent = self._format_exponent(fmt)
        if 'tex' in fmt.lower():
            if self.base == '#':
                return rf"${coefficient}{self.base}{exponent}$"
            return rf"${coefficient}\mathrm{{{self.base}}}{exponent}$"
        return f"{coefficient}{self.base}{exponent}"

    def _format_coefficient(self):
        """Format the coefficient for printing."""
        if self.base != '1' and self.coefficient == 1:
            return ''
        if self._ambiguous_coefficient():
            return f"({self.coefficient})"
        if float(self.coefficient) == int(self.coefficient):
            return str(int(self.coefficient))
        return str(self.coefficient)

    def _ambiguous_coefficient(self):
        """True if this term's coefficient needs to be grouped."""
        return (
            isinstance(self.coefficient, fractions.Fraction)
            and self.base != '1'
            and self.coefficient.denominator != 1
        )

    def _format_exponent(self, style: str):
        """Format the current exponent for printing."""
        if self.base == '1' or self.exponent == 1:
            return ''
        if not style:
            return f"^{self.exponent}"
        if 'tex' in style.lower():
            return f"^{{{self.exponent}}}"
        raise ValueError(f"Can't format {self.exponent}")

    def __int__(self):
        """Called for int(self)."""
        return self._cast_to(int)

    def __float__(self):
        """Called for float(self)."""
        return self._cast_to(float)

    _T = typing.TypeVar('_T', int, float)

    def _cast_to(self, __type: _T) -> _T:
        """Internal method for casting to numeric type."""
        if self.base == '1':
            return __type(self.coefficient)
        errmsg = f"Can't convert term with base {self.base!r} to {__type}"
        raise TypeError(errmsg) from None

    def __eq__(self, other) -> bool:
        if isinstance(other, numbers.Real):
            return float(self) == float(other)
        if isinstance(other, str):
            term = OperandFactory().create(other)
            return super().__eq__(term)
        return super().__eq__(other)

    def __hash__(self) -> int:
        # NOTE: If we decide to implement `Operand.__hash__`, we will still need
        # to explicitly define `Term.__hash__`. See
        # https://docs.python.org/3/reference/datamodel.html#object.__hash__ for
        # an explanation.
        return hash(self.attrs)


@typing.overload
def term_factory(base: str, /) -> Term:
    """Create a symbolic term from a base quantity.
    
    Parameters
    ----------
    base : string
        The base quantity of this symbolic term.
    """

@typing.overload
def term_factory(
    coefficient: numbers.Real=1,
    base: str='1',
    exponent: numbers.Real=1,
) -> Term:
    """Create a symbolic term from coefficient, base, and exponent.
    
    Parameters
    ----------
    coefficient : real number, default=1
        The numerical coefficient to associate with the base quantity.

    base : string, default='1'
        The base quantity of this symbolic term.

    exponent : real number, default=1
        The exponent of the base quantity.
    """

def term_factory(*args, **kwargs):
    """Factory function for symbolic terms."""
    if not kwargs:
        # positional argument(s) only
        if not args:
            # use all default values
            return Term()
        if len(args) == 1:
            # single-argument form (positional base only)
            base = args[0]
            _validate_term_base(base)
            return Term(base=base)
        if len(args) == 3:
            # triple-argument form
            base = args[1]
            _validate_term_base(base)
            return Term(*args)
    if not args:
        # keyword arguments only
        if 'base' in kwargs:
            # NOTE: We don't use `base = kwargs.get('base')` because we
            # don't want to mistakenly treat `None` as the base when
            # comparing to the base RE pattern. We'll let `Operand`
            # determine the default value.
            _validate_term_base(kwargs['base'])
        return Term(**kwargs)
    raise TypeError(
        f"Cannot create a symbolic term from {args} and {kwargs}."
    ) from None


def _validate_term_base(base):
    """Raise an exception if `base` does not match the definition."""
    if not Term.base_is_valid(base):
        raise ValueError(
            f"Cannot create a symbolic term with base {base!r}"
        ) from None


def asterms(these: typing.Iterable[str]):
    """Convert strings to terms, if possible."""
    return [OperandFactory().create(this) for this in these]


