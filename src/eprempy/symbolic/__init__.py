import typing

from ._expression import (
    Expression,
    expression_factory as expression,
    reduce,
    standard,
)
from ._operand import (
    asterms,
    OperandFactory,
    OperandTypeError,
    OperandValueError,
    Term,
    term_factory as term,
)
from ._parser import (
    ParsingValueError,
    ProductError,
    RatioError,
)

__all__ = [
    'Expression',
    'Expressable',
    'OperandFactory',
    'OperandTypeError',
    'OperandValueError',
    'ParsingValueError',
    'ProductError',
    'RatioError',
    'Term',
    'asterms',
    'expression',
    'reduce',
    'standard',
    'term',
]


Expressable = typing.TypeVar(
    'Expressable',
    str,
    typing.Iterable,
    Expression,
)
Expressable = typing.Union[str, typing.Iterable, Expression]


def composition(this):
    """True if `this` appears to be a symbolic composition of terms.
    
    Parameters
    ----------
    this
        The object to check.

    Notes
    -----
    This is more stringent than simply checking whether `this` can instantiate a
    `~symbolic.Expression` because any string would satisfy that condition.
    """
    return (
        isinstance(this, Expression)
        or isinstance(this, str) and ('/' in this or '*' in this)
    )


def equality(a, b) -> Expression:
    """Symbolically compute a == b."""
    x, y = (expression(i) for i in (a, b))
    return x == y


def product(a, b) -> Expression:
    """Symbolically compute a * b."""
    x, y = (expression(i) for i in (a, b))
    return x * y


def ratio(a, b) -> Expression:
    """Symbolically compute a / b."""
    x, y = (expression(i) for i in (a, b))
    return x / y


def power(a, n) -> Expression:
    """Symbolically compute a ** n."""
    return expression(a) ** n
