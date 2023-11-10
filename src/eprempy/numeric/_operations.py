import typing

from .. import aliased
from .. import container
from . import _operators


T = typing.TypeVar('T')


_OPERATION_METADATA = {
    'int': {
        'builtin': int,
        'forward': _operators.__int__,
    },
    'float': {
        'builtin': float,
        'forward': _operators.__float__,
    },
    'complex': {
        'builtin': complex,
        'forward': _operators.__complex__,
    },
    'eq': {
        'builtin': _operators.eq,
        'forward': _operators.__eq__,
        'aliases': [
            'equal',
        ],
    },
    'ne': {
        'builtin': _operators.ne,
        'forward': _operators.__ne__,
        'aliases': [
            'not equal',
            'unequal',
        ],
    },
    'lt': {
        'builtin': _operators.lt,
        'forward': _operators.__lt__,
        'aliases': [
            'less than',
            'less',
        ],
    },
    'le': {
        'builtin': _operators.le,
        'forward': _operators.__le__,
        'aliases': [
            'less than or equal to',
            'less or equal',
        ],
    },
    'gt': {
        'builtin': _operators.gt,
        'forward': _operators.__gt__,
        'aliases': [
            'greater than',
            'greater',
        ],
    },
    'ge': {
        'builtin': _operators.ge,
        'forward': _operators.__ge__,
        'aliases': [
            'greater than or equal to',
            'greater or equal',
        ],
    },
    'abs': {
        'builtin': _operators.abs,
        'forward': _operators.__abs__,
        'aliases': [
            'absolute',
        ],
    },
    'pos': {
        'builtin': _operators.pos,
        'forward': _operators.__pos__,
        'aliases': [
            'positive',
        ],
    },
    'neg': {
        'builtin': _operators.neg,
        'forward': _operators.__neg__,
        'aliases': [
            'negative',
        ],
    },
    'round': {
        'builtin': _operators.round,
        'forward': _operators.__round__,
    },
    'floor': {
        'builtin': _operators.floor,
        'forward': _operators.__floor__,
    },
    'ceil': {
        'builtin': _operators.ceil,
        'forward': _operators.__ceil__,
        'aliases': [
            'ceiling',
        ],
    },
    'trunc': {
        'builtin': _operators.trunc,
        'forward': _operators.__trunc__,
        'aliases': [
            'truncate',
        ],
    },
    'add': {
        'builtin': _operators.add,
        'forward': _operators.__add__,
        'reverse': _operators.__radd__,
        'inplace': _operators.__iadd__,
        'aliases': [
            'addition',
        ],
    },
    'sub': {
        'builtin': _operators.sub,
        'forward': _operators.__sub__,
        'reverse': _operators.__rsub__,
        'inplace': _operators.__isub__,
        'aliases': [
            'subtraction',
            'subtract',
        ],
    },
    'mul': {
        'builtin': _operators.mul,
        'forward': _operators.__mul__,
        'reverse': _operators.__rmul__,
        'inplace': _operators.__imul__,
        'aliases': [
            'multiplication',
            'multiply',
        ],
    },
    'truediv': {
        'builtin': _operators.truediv,
        'forward': _operators.__truediv__,
        'reverse': _operators.__rtruediv__,
        'inplace': _operators.__itruediv__,
        'aliases': [
            'true divide',
            'true_divide',
            'divide',
            'division',
            'true division',
            'floating-point division',
        ],
    },
    'floordiv': {
        'builtin': _operators.floordiv,
        'forward': _operators.__floordiv__,
        'reverse': _operators.__rfloordiv__,
        'inplace': _operators.__ifloordiv__,
        'aliases': [
            'floor divide',
            'floor_divide',
            'floor division',
        ],
    },
    'mod': {
        'builtin': _operators.mod,
        'forward': _operators.__mod__,
        'reverse': _operators.__rmod__,
        'inplace': _operators.__imod__,
        'aliases': [
            'mod',
            'remainder',
        ],
    },
    'pow': {
        'builtin': _operators.pow,
        'forward': _operators.__pow__,
        'reverse': _operators.__rpow__,
        'inplace': _operators.__ipow__,
        'aliases': [
            'power',
        ],
    },
}
_OPERATIONS = aliased.Mapping(_OPERATION_METADATA)
"""An aliased collection of operations."""


IMPLEMENTATIONS = aliased.Mapping(
    {
        (k, *v.get('aliases', [])): [m for n, m in v.items() if n != 'aliases']
        for k, v in _OPERATION_METADATA.items()
    }
)
"""An aliased mapping of callable operator implementations."""


FUNCTIONS = aliased.Mapping(
    {
        (k, *v.get('aliases', [])): v['builtin']
        for k, v in _OPERATION_METADATA.items()
    }
)
"""An aliased mapping of operator functions."""


METHODS = aliased.Mapping(
    {
        (k, *v.get('aliases', [])): [
            m for n, m in v.items() if n not in {'aliases', 'builtin'}
        ]
        for k, v in _OPERATION_METADATA.items()
    }
)
"""An aliased mapping of operator dunder methods."""


_DUNDER_MAP = {
    '__int__': _operators.__int__,
    '__float__': _operators.__float__,
    '__complex__': _operators.__complex__,
    '__eq__': _operators.__eq__,
    '__ne__': _operators.__ne__,
    '__lt__': _operators.__lt__,
    '__gt__': _operators.__gt__,
    '__le__': _operators.__le__,
    '__ge__': _operators.__ge__,
    '__abs__': _operators.__abs__,
    '__pos__': _operators.__pos__,
    '__neg__': _operators.__neg__,
    '__round__': _operators.__round__,
    '__floor__': _operators.__floor__,
    '__ceil__': _operators.__ceil__,
    '__trunc__': _operators.__trunc__,
    '__add__': _operators.__add__,
    '__radd__': _operators.__radd__,
    '__sub__': _operators.__sub__,
    '__rsub__': _operators.__rsub__,
    '__mul__': _operators.__mul__,
    '__rmul__': _operators.__rmul__,
    '__truediv__': _operators.__truediv__,
    '__rtruediv__': _operators.__rtruediv__,
    '__floordiv__': _operators.__floordiv__,
    '__rfloordiv__': _operators.__rfloordiv__,
    '__mod__': _operators.__mod__,
    '__rmod__': _operators.__rmod__,
    '__pow__': _operators.__pow__,
    '__rpow__': _operators.__rpow__,
}

DUNDER = container.Bijection(_DUNDER_MAP)


_CALLABLE_MAP = {k: v['builtin'] for k, v in _OPERATION_METADATA.items()}

CALLABLES = container.Bijection(_CALLABLE_MAP)


_OPERATOR_GROUPS = {
    'cast': ['int', 'float', 'complex'],
    'unary': ['abs', 'pos', 'neg'],
    'ordering': ['lt', 'le', 'gt', 'ge'],
    'additive': ['add', 'sub'],
    'multiplicative': ['mul', 'truediv'],
    'math': ['floor', 'ceil', 'trunc'],
}
_OPERATOR_GROUPS['comparative'] = [
    *_OPERATOR_GROUPS['ordering'],
    'eq',
    'ne',
]
_OPERATOR_GROUPS['algebraic'] = [
    *_OPERATOR_GROUPS['additive'],
    *_OPERATOR_GROUPS['multiplicative'],
    'pow',
]
_OPERATOR_GROUPS['binary'] = [
    *_OPERATOR_GROUPS['comparative'],
    *_OPERATOR_GROUPS['additive'],
    *_OPERATOR_GROUPS['multiplicative'],
]
_OPERATOR_GROUPS['real'] = [
    *_OPERATOR_GROUPS['comparative'],
    *_OPERATOR_GROUPS['algebraic'],
    *_OPERATOR_GROUPS['unary'],
    'floordiv',
    'mod',
]
_OPERATOR_GROUPS['scalar'] = [
    *_OPERATOR_GROUPS['real'],
    'round',
]


def _build_operators():
    """Internal function for building the default collection of operators.
    
    This function exists solely to reduce the scope of intermediate objects. It
    is not for public use.

    See Also
    --------
    `~OPERATORS`
        An immutable aliased mapping of default operators.
    `~get`
        A function for retrieving operators or operator groups by name.
    """
    _builtins = {
        key: operator['builtin']
        for key, operator in _OPERATIONS.items(aliased=True)
    }
    _operators = aliased.MutableMapping(_builtins)
    for name, keys in _OPERATOR_GROUPS.items():
        _operators.group(name, *keys)
    return _operators


class Mapping(aliased.Mapping):
    """A callable aliased mapping of numeric operators."""

    def __init__(self, mapping: typing.Mapping):
        if isinstance(mapping, aliased.MutableMapping):
            super().__init__(mapping.freeze(groups=True))
            self._groups = mapping._groups.copy()
        else:
            super().__init__(mapping)

    def callgroup(self, key: str, *args, **kwargs):
        """Compute the result of each operation in a group."""
        if key not in self._groups:
            raise KeyError(
                f"Unknown operator group: {key!r}"
            ) from None
        names = self._groups[key]
        operators = self[key]
        pairs = zip(names, operators)
        if len(args) == 1:
            for name in names:
                if name not in self._groups['unary']:
                    raise ValueError(
                        f"Cannot compute non-unary operation {name!r}"
                        " to a single argument"
                    ) from None
            arg = args[0]
            return {k: f(arg, **kwargs) for (k, f) in pairs}
        return {
            k: self._compute(k, f, *args, **kwargs)
            for (k, f) in zip(names, operators)
        }

    def _compute(self, name, f, *args, **kwargs):
        """Helper for `~callgroup`."""
        if name in self._groups['unary']:
            return tuple(f(arg, **kwargs) for arg in args)
        return f(*args, **kwargs)

    def __call__(self, key: str, *args, **kwargs):
        """Compute the result of an operation on the given arguments."""
        try:
            r = self[key]
        except KeyError as err:
            raise ValueError(
                f"Unknown operator or group: {key!r}"
            ) from err
        if isinstance(r, tuple):
            return tuple([f(*args, **kwargs) for f in r])
        return r(*args, **kwargs)

    def generate(self, *names: str, excluded: typing.Iterable[str]=None):
        """Retrieve standard operators or operator groups by name.
        
        Parameters
        ----------
        *names : strings
            The names of requested operators or operator groups. If missing,
            this function will produce all standard operators.

        excluded : iterable of strings, optional
            Names of operators to exclude.

        Notes
        -----
        The available operator groups and their corresponding operators are

        * `'unary'`: `['abs', 'pos', 'neg']`,
        * `'comparative'`: `['eq', 'ne', 'lt', 'le', 'gt', 'ge']`,
        * `'additive'`: `['add', 'sub']`,
        * `'multiplicative'`: `['mul', 'truediv', 'floordiv', 'mod']`,

        See Also
        --------
        `~OPERATORS`
            An immutable aliased mapping of default operators.
        """
        if not names:
            yield from self.values()
        keys = []
        for name in names:
            if name in self._groups:
                keys.extend(self._groups[name])
            else:
                keys.append(name)
        values = (self[key] for key in set(keys) - set(excluded or ()))
        yield from values


_OPERATORS = Mapping(_build_operators())
"""An aliased collection of canonical numeric operators."""


@typing.overload
def resolve(
    operation,
    strict: typing.Optional[bool],
) -> typing.Optional[typing.Callable]: ...

@typing.overload
def resolve(
    operation,
    strict: typing.Literal[True],
) -> typing.Callable: ...

def resolve(operation, strict: bool=False):
    """Get the callable operator corresponding to `operation`."""
    if not (isinstance(operation, str) or callable(operation)):
        raise TypeError(operation)
    if operation in _OPERATORS.values():
        return operation
    if found := _OPERATORS.get(operation):
        return found
    if strict:
        raise ValueError(
            f"Cannot determine appropriate operator for {operation!r}"
        ) from None


class OperandTypeError(TypeError):
    """Wrong operand type for a numeric operation."""


