import numpy
import pytest

from eprempy import numeric
from eprempy.numeric import _operators as f


@pytest.fixture
def operations():
    """The operations defined on numeric objects."""
    return {
        ('eq', 'equal'): f.eq,
        ('not equal', 'ne', 'unequal'): f.ne,
        ('less', 'lt', 'less than'): f.lt,
        ('less than or equal to', 'le', 'less or equal'): f.le,
        ('greater', 'greater than', 'gt'): f.gt,
        ('greater or equal', 'ge', 'greater than or equal to'): f.ge,
        ('absolute', 'abs'): f.abs,
        ('pos', 'positive'): f.pos,
        ('neg', 'negative'): f.neg,
        ('round', 'round'): f.round,
        ('floor', 'floor'): f.floor,
        ('ceil', 'ceil'): f.ceil,
        ('truncate', 'trunc'): f.trunc,
        ('addition', 'add'): f.add,
        ('subtract', 'subtraction', 'sub'): f.sub,
        ('multiply', 'multiplication', 'mul'): f.mul,
        ('divide', 'true_divide', 'truediv', 'true divide'): f.truediv,
        ('floor_divide', 'floordiv', 'floor divide'): f.floordiv,
        ('mod', 'remainder'): f.mod,
        ('power', 'pow'): f.pow,
    }


@pytest.fixture
def operator_groups():
    """Defined groups of numeric operators."""
    groups = {
        'unary': ['abs', 'pos', 'neg'],
        'ordering': ['lt', 'le', 'gt', 'ge'],
        'additive': ['add', 'sub'],
        'multiplicative': ['mul', 'truediv'],
        'math': ['floor', 'ceil', 'trunc'],
    }
    groups['comparative'] = [*groups['ordering'], 'eq', 'ne']
    groups['algebraic'] = [
        *groups['additive'],
        *groups['multiplicative'],
        'pow',
    ]
    groups['binary'] = [
        *groups['comparative'],
        *groups['additive'],
        *groups['multiplicative'],
    ]
    groups['real'] = [
        *groups['comparative'],
        *groups['algebraic'],
        *groups['unary'],
        'floordiv',
        'mod',
    ]
    groups['scalar'] = [*groups['real'], 'round']
    return groups


class Object(numeric.Object):
    """A numeric object for tests."""

    def __init__(self, data, color) -> None:
        super().__init__(data)
        self.color = color

    def __eq__(self, other) -> bool:
        if isinstance(other, Object):
            return (
                numpy.array_equal(self.data, other.data)
                and
                self.color == other.color
            )
        return False

    def __ne__(self, other) -> bool:
        return not (self == other)


class Functions(Object, numeric.Functions):
    """A test object with custom `numpy` function support."""
    _FUNCTIONS = {}

@Functions.implements(numpy.sqrt)
def _numpy_sqrt(x: Functions, /):
    return Functions(numpy.sqrt(x.data), x.color)

@Functions.implements(numpy.mean)
def _numpy_mean(x: Functions, *args, **kwargs):
    return Functions(numpy.mean(x.data, *args, **kwargs), x.color)


@pytest.fixture
def object_factory():
    """Factory for test objects."""
    def factory(data, color):
        return Object(data, color)
    return factory


@pytest.fixture
def functions_factory():
    """Factory for test instances of the `numeric.Functions` mixin."""
    def factory(data, color):
        return Functions(data, color)
    return factory


