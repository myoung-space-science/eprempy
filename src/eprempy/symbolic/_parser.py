import typing

from . import _operand
from . import _operator


class ParsingError(Exception):
    """Base class for exceptions encountered during symbolic parsing."""

    def __init__(self, arg: typing.Any) -> None:
        self.arg = arg


class RatioError(ParsingError):
    """The string contains multiple '/' on a single level."""

    def __str__(self) -> str:
        return (
            f"The expression '{self.arg}' contains ambiguous '/'."
            f" Please refer to the NIST guidelines"
            f" (https://physics.nist.gov/cuu/Units/checklist.html)"
            f" for more information."
        )


class ProductError(ParsingError):
    """The string contains a '*' after a '/'."""

    def __str__(self) -> str:
        return (
            f"The expression '{self.arg}' contains an ambiguous '*'."
            f" Please group '*' in parentheses when following '/'."
        )


class ParsingValueError(ValueError):
    """Cannot create an expression from the given string."""
    pass


class Iteration:
    """An object that keeps track of parsing attributes."""

    __slots__ = ('string', 'operator', 'operand')

    def __init__(
        self,
        string: str,
        operator: _operator.Operator=None,
        operand: _operand.Operand=None,
    ) -> None:
        self.string = string
        self.operator = operator
        self.operand = operand

    @property
    def _attrs(self):
        """Internal mapping of current attribute values."""
        return {name: getattr(self, name) for name in self.__slots__}

    def copy(self):
        """Make a copy of this instance."""
        return type(self)(**self._attrs)

    def __str__(self):
        """A simplified representation of this object."""
        return ', '.join(f"{k}={v!r}" for k, v in self._attrs.items())

    def __repr__(self):
        """An unambiguous representation of this object."""
        return f"{self.__class__.__qualname__}({self})"


class Parser:
    """A tool for parsing symbolic expressions."""

    def __init__(
        self,
        multiply: str='*',
        divide: str='/',
        opening: str='(',
        closing: str=')',
        raising: str='^',
        operator_order: str='ignore',
    ) -> None:
        """
        Initialize a parser with fixed tokens.

        Parameters
        ----------
        multiply : string, default='*'
            The token that represents multiplication.

        divide : string, default='/'
            The token that represents division.

        opening : string, default='('
            The token that represents an opening separator.

        closing : string, default='('
            The token that represents a closing separator.

        raising : string, default='^'
            The token that represents raising to a power (exponentiation).

        operator_order : {'ignore', 'error'}
            Determines how the parser responds when operator order violates NIST
            guidelines. If set to `'ignore'` (default), it will treat operators
            independent of one another. If set to `'error'`, the parser will
            raise an exception based on the type of violation.
        """
        self.operands = _operand.OperandFactory(opening, closing, raising)
        self.operators = _operator.OperatorFactory(multiply, divide)
        self.parsers = (self.operands, self.operators)
        self.tokens = {
            'multiply': multiply,
            'divide': divide,
            'opening': opening,
            'closing': closing,
            'raising': raising,
        }
        self._operator_order = operator_order

    def parse(self, string: str):
        """Resolve the given string into individual terms."""
        operand = _operand.Operand(base=string)
        return self._resolve_operations(operand)

    def _resolve_operations(
        self,
        current: _operand.Operand,
    ) -> typing.List[_operand.Term]:
        """Separate a symbolic group into operators and operands."""
        operands = self._parse_operand(current)
        return [
            t for operand in operands
            for t in self._update_terms(operand)
        ] + [_operand.term_factory(coefficient=current.coefficient)]

    def _parse_operand(
        self,
        initial: _operand.Operand,
    ) -> typing.List[_operand.Operand]:
        """Resolve a general operand into simpler operands.

        This method parses known operators and operands from the initial operand
        while preserving nested groups in the latter. Calling code may then pass
        those nested groups back in for further parsing.
        """
        operands = []
        current = Iteration(initial.base)
        previous = current.copy()
        while current.string:
            current = self._get_operator(initial, current, previous)
            current = self._get_operand(initial, current)
            if new := self._compute_operand(current):
                operands.append(new)
            previous = current.copy()
            current = Iteration(previous.string)
        return operands

    def _get_operator(
        self,
        initial: _operand.Operand,
        current: Iteration,
        previous: Iteration,
    ) -> Iteration:
        """Attempt to parse an operator from the current string."""
        if parsed := self.operators.parse(current.string):
            current.operator = parsed.result
            if exception := self._operator_error(
                    current.operator,
                    previous.operator,
                ): raise exception(initial)
            current.string = parsed.remainder
        return current

    def _get_operand(
        self,
        initial: _operand.Operand,
        current: Iteration,
    ) -> Iteration:
        """Attempt to parse an operand from the current string."""
        if parsed := self.operands.parse(current.string):
            current.operand = parsed.result ** initial.exponent
            current.string = parsed.remainder
        return current

    def _compute_operand(self, current: Iteration):
        """Create a new operand from the current iteration."""
        if current.operand and current.operator:
            return self._evaluate(current.operator, current.operand)
        if current.operand:
            return current.operand
        if current.operator:
            raise ParsingValueError("Operator without operand")
        raise ParsingValueError("Failed to parse string")

    def _operator_error(
        self,
        current: _operator.Operator,
        previous: _operator.Operator,
    ) -> typing.Optional[typing.Type[ParsingError]]:
        """Check for known operator-related errors.
        
        This method checks for the following errors and returns the appropriate
        exception class if it finds one:

        - Multiple divisions on a single level (e.g., `'a / b / c'`), which
          results in a `RatioError`.

        - Multiplication after division on the same level (e.g., `'a / b * c'`),
          which results in a `ProductError`.

        Both of the examples shown above result in errors because they each
        introduce an ambiguous order of operations. Users can resolve the
        ambiguity by properly grouping terms in the expression. Continuing with
        the above examples, `'a / b / c'` should become `'(a / b) / c'` or `'a /
        (b / c)'`, and `'a / b * c'` should become `'(a / b) * c'` or `'a / (b *
        c)'`.
        """
        if self._operator_order == 'ignore':
            return
        if previous == 'divide':
            if current == 'divide':
                return RatioError
            if current == 'multiply':
                return ProductError

    def _evaluate(
        self,
        operator: _operator.Operator,
        operand: _operand.Operand,
    ) -> _operand.Operand:
        """Compute the effect of `operator` on `operand`."""
        if operator in {'multiply', 'identity'}:
            return operand
        if operator == 'divide':
            return operand ** -1
        if operator == 'sqrt':
            return operand ** 0.5
        raise ValueError(f"Unrecognized operator {operator!r}")

    def _update_terms(self, operand: _operand.Operand):
        """Store a new term or initiate further parsing."""
        # TODO: Consider extracting all coefficients, at least as separate
        # constant terms.
        if isinstance(operand, _operand.Term):
            return [operand]
        return self._resolve_operations(operand)


