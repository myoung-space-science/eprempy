import re

from . import _part


class Operator(_part.Part):
    """An operator in a symbolic expression."""

    def __init__(self, operation: str) -> None:
        self.operation = operation

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return self.operation

    def __hash__(self) -> str:
        """Compute instance hash (e.g., for use as `dict` key)."""
        return hash(self.operation)

    def __eq__(self, other) -> bool:
        """True if two operators represent the same operation."""
        if isinstance(other, Operator):
            return other.operation == self.operation
        if isinstance(other, str):
            return other == self.operation
        return NotImplemented


class OperatorFactory(_part.Factory):
    """A factory that produces symbolic operators."""

    def __init__(
        self,
        multiply: str='*',
        divide: str='/',
    ) -> None:
        mul = fr'\{multiply}'
        div = fr'\{divide}'
        self.patterns = {
            'multiply': re.compile(
                fr'(?<!{div})(\s*{mul}\s*)(?!{div})'
            ),
            'divide': re.compile(
                fr'(?<!{mul})(\s*{div}\s*)(?!{mul})'
            ),
            'sqrt': re.compile(r'\s*sqrt\s*')
        }
        """Compiled regular expressions for symbolic operators."""

    def parse(self, string: str):
        """Extract an operator at the start of `string`, possible."""
        for key in self.patterns:
            if match := self.patterns[key].match(string):
                return _part.Match(
                    result=Operator(key),
                    context=match,
                )


