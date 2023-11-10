import typing

from eprempy import numeric


def test_operators_mapping(operations):
    """Test the default collection of operators."""
    for operation in operations:
        for key in operation:
            assert key in numeric.OPERATORS


def test_generate_operators(
    operations: typing.Dict[typing.Tuple[str], typing.Callable],
    operator_groups: typing.Dict[str, typing.List[str]],
) -> None:
    """Test the function that retrieves operators by name."""
    for operation, operator in operations.items():
        for key in operation:
            assert set(numeric.OPERATORS.generate(key)) == {operator}
    for key, names in operator_groups.items():
        operators = [numeric.OPERATORS[operation] for operation in names]
        assert set(numeric.OPERATORS.generate(key)) == set(operators)


def test_call_operators() -> None:
    """Test the ability to call the operators object."""
    named = {
        'eq':       ((2, 3), False),
        'ne':       ((2, 3), True),
        'lt':       ((2, 3), True),
        'le':       ((2, 3), True),
        'gt':       ((2, 3), False),
        'ge':       ((2, 3), False),
        'abs':      ((-3,), 3),
        'pos':      ((-3,), -3),
        'neg':      ((-3,), 3),
        'add':      ((5, 2), 7),
        'sub':      ((5, 2), 3),
        'mul':      ((5, 2), 10),
        'truediv':  ((5, 2), 2.5),
        'floordiv': ((5, 2), 2),
        'mod':      ((5, 2), 1),
        'pow':      ((5, 2), 25),
    }
    for key, (args, result) in named.items():
        assert numeric.OPERATORS(key, *args) == result


def test_callgroup():
    """Test the operator-mapping `callgroup` method."""
    x, y = 2, -4
    testable ={
        'comparative': {
            'lt': x < y,
            'le': x <= y,
            'gt': x > y,
            'ge': x >= y,
            'eq': x == y,
            'ne': x != y,
        },
        'additive': {
            'add': x + y,
            'sub': x - y,
        },
        'multiplicative' : {
            'mul': x * y,
            'truediv': x / y,
        },
        'unary': {
            'abs': (2, 4),
            'pos': (2, -4),
            'neg': (-2, 4),
        },
    }
    testable['binary'] = {
        **testable['comparative'],
        **testable['additive'],
        **testable['multiplicative'],
    }
    testable['real'] = {
        **testable['unary'],
        **testable['binary'],
        'floordiv': x // y,
        'mod': x % y,
        'pow': x ** y,
    }
    for key, expected in testable.items():
        assert numeric.OPERATORS.callgroup(key, 2, -4) == expected


