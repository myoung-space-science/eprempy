import collections.abc
import functools
import itertools
import typing

import numpy
import numbers

from . import etc


T = typing.TypeVar('T')


def unique(*args: T, strict: bool=False) -> typing.List[T]:
    """Remove repeated items from `args` while preserving order.
    
    Parameters
    ----------
    *args
        The items to compare.

    strict : bool, default=false
        By default, if `args` comprises a single iterable object, this function
        will extract that object under the assumption that the caller wants to
        remove repeated items from the given iterable object. If `strict` is
        true, this function will operate on the input as given.
    """
    items = (
        args[0] if (not strict and len(args) == 1)
        else args
    )
    collection = []
    for item in items:
        if item not in collection:
            collection.append(item)
    return collection


_Wrapped = typing.TypeVar('_Wrapped', bound=typing.Iterable)


@typing.overload
def unwrap(obj: typing.Union[T, typing.Iterable[T]]) -> T: ...


@typing.overload
def unwrap(
    obj: typing.Union[T, typing.Iterable[T]],
    newtype: typing.Type[_Wrapped]=None,
) -> _Wrapped: ...


def unwrap(obj, newtype=None):
    """Remove redundant outer lists and tuples.

    This function will strip away enclosing instances of `list` or `tuple`, as
    long as they contain a single item, until it finds an object of a different
    type, a `list` or `tuple` containing multiple items, or an empty `list` or
    `tuple`.

    Parameters
    ----------
    obj : Any
        The object to "unwrap".

    newtype : type
        An iterable type into which to store the result. Specifying this allows
        the caller to ensure that the result is an iterable object after
        unwrapping interior iterables.

    Returns
    -------
    Any
        The element enclosed in multiple instances of `list` or `tuple`, or a
        (possibly empty) `list` or `tuple`.

    Examples
    --------
    Unwrap numbers enclosed in increasingly deeper lists:

    >>> cases = [[1], [[2]], [[[3]]], [[[[4]]]]]
    >>> for case in cases:
    ...     print(unwrap(case))
    ... 
    1
    2
    3
    4

    It preserves numbers and strings that are already unwrapped:

    >>> unwrap(42)
    42
    >>> unwrap('string')
    'string'

    Passing a type to `newtype` ensures a result of that type:

    >>> unwrap(42, newtype=tuple)
    (42,)
    >>> unwrap(42, newtype=list)
    [42]
    >>> unwrap([42], newtype=list)
    [42]
    >>> unwrap(([(42,)],), newtype=list)
    [42]

    It works with multiple wrapped elements:

    >>> unwrap([1, 2])
    [1, 2]
    >>> unwrap([[1, 2]])
    [1, 2]
    >>> unwrap(['one', 'two'])
    ['one', 'two']
    >>> unwrap([['one', 'two']])
    ['one', 'two']

    It stops at an empty `list` or `tuple`:

    >>> unwrap([])
    []
    >>> unwrap(())
    ()
    >>> unwrap(list())
    []
    >>> unwrap(tuple())
    ()
    >>> unwrap([[]])
    []
    >>> unwrap([()])
    ()
    >>> unwrap([], newtype=tuple)
    ()
    """
    seed = [obj]
    wrapped = (list, tuple)
    while isinstance(seed, wrapped) and len(seed) == 1:
        seed = seed[0]
    if newtype is not None:
        return newtype(wrap(seed))
    return seed


def wrap(
    arg: typing.Optional[typing.Union[T, typing.Iterable[T]]],
) -> typing.List[T]:
    """Wrap `arg` in a list, if necessary.

    In most cases, this function will try to iterate over `arg`. If that
    operation succeeds, it will simply return `arg`; if the attempt to iterate
    raises a `TypeError`, it will assume that `arg` is a scalar and will return
    a one-element list containing `arg`. If `arg` is `None`, this function will
    return an empty list. If `arg` is a string, this function will return a
    one-element list containing `arg`.
    """
    if arg is None:
        return []
    if isinstance(arg, str):
        return [arg]
    try:
        iter(arg)
    except TypeError:
        return [arg]
    else:
        return list(arg)


class Wrapper(collections.abc.Collection, typing.Generic[T]):
    """A collection of independent members.

    This class represents an iterable collection with members that have meaning
    independent of any other members. When initialized with a "separable" object
    (e.g., a `list`, `tuple`, or `set`), the new instance will behave like the
    equivalent `tuple`. When initialized with a non-"separable" object, the new
    instance will behave like a `tuple` containing that object.

    See Also
    --------
    `~isseparable`
    """

    def __init__(
        self,
        this: typing.Optional[typing.Union[T, typing.Iterable[T]]],
        /,
    ) -> None:
        """Initialize a wrapped object from `this`"""
        self._arg = this
        self._wrapped = tuple(wrap(this))

    def __iter__(self) -> typing.Iterator[T]:
        """Called for iter(self)."""
        return iter(self._wrapped)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self._wrapped)

    def __contains__(self, __x: object) -> bool:
        """Called for __x in self."""
        return __x in self._wrapped

    def __eq__(self, other) -> bool:
        """True if two wrapped objects have equal arguments."""
        if isinstance(other, Wrapper):
            return sorted(self) == sorted(other)
        return NotImplemented

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return self._arg


def isseparable(x, /):
    """True if `x` is iterable but is not string-like.

    This function identifies iterable collections with members that have meaning
    independent of any other members. For example, a list of numbers is
    "separable" whereas a string is not, despite the fact that both objects are
    iterable collections.

    The motivation for this distinction is to make it easier to treat single
    numbers and strings equivalently to iterables of numbers and strings.
    """
    try:
        iter(x)
    except TypeError:
        return False
    return not isinstance(x, (str, bytes))


def hastype(
    __obj,
    __types: typing.Union[type, typing.Tuple[type, ...]],
    *wrappers: typing.Type[typing.Iterable],
    strict: bool=False,
) -> bool:
    """True if an object is a certain type or contains certain types.
    
    Parameters
    ----------
    __obj : Any
        The object to compare.

    __types : type or tuple of types
        One or more types of which the target object may be an instance.

    *wrappers : iterable type
        Zero or more iterable types of which the target object may be an
        instance. If the target object is an instance of a given wrapper type,
        this function will test whether every member of the target object is an
        instance of the given types.

    strict : bool, default=False
        If true, return `True` if `__obj` contains only members with the target
        type(s). Otherwise, return `True` if `__obj` contains at least one
        member with the target type(s).

    Examples
    --------
    When called without wrappers, this function is identical to `isinstance`:

    >>> iterables.hastype(1, int)
    True

    >>> iterables.hastype('s', str)
    True

    >>> iterables.hastype([1, 2], list)
    True

    Note that in these cases, `strict` is irrelevant because this function
    checks only the type of `__obj`.

    The target object contains the given type but `list` is not a declared
    wrapper:
    
    >>> iterables.hastype([1, 2], int)
    False
    
    Same as above, but this time `list` is a known wrapper:

    >>> iterables.hastype([1, 2], int, list)
    True
    
    Similar, except only `tuple` is declared as a wrapper:

    >>> iterables.hastype([1, 2], int, tuple)
    False

    By default, only one member of a wrapped object needs to be an instance of
    one of the target types:

    >>> iterables.hastype([1, 2.0], int, list)
    True

    If `strict=True`, each member must be one of the target types:

    >>> iterables.hastype([1, 2.0], int, list, strict=True)
    False

    Multiple target types must be passed as a `tuple`, just as when calling
    `isinstance`:

    >>> iterables.hastype([1, 2.0], (int, float), list)
    True

    Otherwise, this function will interpret them as wrapper types:

    >>> iterables.hastype([1, 2.0], int, float, list, strict=True)
    False
    """
    if isinstance(__obj, __types):
        return True
    for wrapper in wrappers:
        if isinstance(__obj, wrapper):
            check = all if strict else any
            return check(isinstance(i, __types) for i in __obj)
    return False


def find_first(__type: typing.Type[T], *args):
    """Find the first argument with the given type."""
    for arg in args:
        if isinstance(arg, __type):
            return arg


@etc.str2repr
class Graph(collections.abc.Collection):
    """A collection of weighted edges."""

    def __init__(self, base: typing.Mapping=None) -> None:
        """Initialize an instance.

        Parameters
        ----------
        base : mapping, optional
            The mapping of weighted connections from which to initialize this
            instance. Items in the mapping must have the form `((start, end),
            weight)`.
        """
        self.connections: typing.Dict[typing.Tuple[str, str], float] = {}
        """The forward and reverse links in this graph."""
        base = base or {}
        for (start, end), weight in base.items():
            self.add_connection(start, end, weight)

    def __contains__(self, connection: typing.Tuple[str, str]):
        """True if `connection` is available."""
        return connection in self.connections

    def __len__(self) -> int:
        """The number of connections. Called for len(self)."""
        return len(self.connections)

    def __iter__(self):
        """Iterate over connections. Called for iter(self)."""
        return iter(self.connections)

    @property
    def nodes(self):
        """The distinct nodes in this graph."""
        return {n for connection in self.connections for n in connection}

    def get_adjacencies(self, node: str):
        """Retrieve the connections to this node.
        
        Parameters
        ----------
        node : string
            The key corresponding to the target node.

        Returns
        -------
        `~dict`
            A dictionary whose keys represent the nodes connected to `node` and
            whose values represent the corresponding edge weight. An empty
            dictionary represents a node with no connections.
        """
        return {
            end: v for (start, end), v in self.connections.items()
            if start == node
        } if node in self.nodes else {}

    def get_weight(self, start: str, end: str):
        """Retrieve the weight of this link, if possible."""
        if (start, end) in self.connections:
            return self.connections[(start, end)]
        raise KeyError(
            f"No connection between {start!r} and {end!r}"
        ) from None

    def add_connection(
        self,
        start: str,
        end: str,
        weight: float=None,
    ) -> None:
        """Add a connection (with optional weight) to the graph."""
        forward = ((start, end), weight)
        inverse = 1 / weight if weight else weight
        reverse = ((end, start), inverse)
        for edge, value in (forward, reverse):
            if edge not in self.connections:
                self.connections[edge] = value

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return '\n'.join(
            f"({n0} -> {n1}): {wt}"
            for (n0, n1), wt in self.connections.items()
        )


class TableKeyError(Exception):
    """No common key with this name."""
    def __str__(self) -> str:
        if len(self.args) > 0:
            return f"Table has no common key '{self.args[0]}'"
        return "Key not found in table"


class TableValueError(Exception):
    """An exception occurred during value-based look-up."""

    def __init__(self, value: typing.Any) -> None:
        self.value = value


class AmbiguousValueError(TableValueError):
    """Failed to find a unique entry by value."""

    def __str__(self) -> str:
        return f"No unique entry containing {self.value!r}"


class MissingValueError(TableValueError):
    """Failed to find any qualifying entries by value."""

    def __str__(self) -> str:
        return f"No entries containing {self.value!r}"


class TableRequestError(Exception):
    """An exception occurred during standard look-up."""

    def __init__(self, request: typing.Mapping) -> None:
        self.request = request


class AmbiguousRequestError(TableRequestError):
    """There are multiple instances of the same value for this key."""

    def __str__(self) -> str:
        """Print the requested pairs in the order provided."""
        items = list(self.request.items())
        n_items = len(items)
        if n_items <= 2:
            requested = " and ".join(f"'{k}={v}'" for k, v in items)
        else:
            these = ", ".join(f"'{k}={v}'" for k, v in items[:-1])
            this = f"'{items[-1][0]}={items[-1][1]}'"
            requested = f"{these}, and {this}"
        if n_items == 1:
            return f"The search criterion {requested} is ambiguous"
        return f"The search criteria {requested} are ambiguous"


class TableLookupError(TableRequestError):
    """Could not find the requested key-value pair(s)."""

    def __str__(self) -> str:
        """Print the requested pairs in the order provided."""
        items = list(self.request.items())
        if len(items) <= 2:
            criteria = " and ".join(f"{k}={v}" for k, v in items)
        else:
            these = ", ".join(f"{k}={v}" for k, v in items[:-1])
            this = f"{items[-1][0]}={items[-1][1]}"
            criteria = f"{these}, and {this}"
        return f"Table has no entry with {criteria}"


class Table(collections.abc.Mapping):
    """A collection of mappings with support for multi-key search.

    Subclasses of this class may override the `_parse` method to customize
    parsing user input into a key-value pair, and the `_prepare` method to
    modify the search result (e.g., cast it to a custom type) before returning.
    """

    _KT = typing.TypeVar('_KT', bound=str)

    _VT = typing.TypeVar('_VT')

    _ET = typing.TypeVar('_ET', bound=typing.Mapping)

    def __init__(self, entries: typing.Collection[_ET]) -> None:
        self._entries = entries
        self._keys = None

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self._entries)

    def __iter__(self) -> typing.Iterator[_ET]:
        """Called for iter(self)."""
        return iter(self._entries)

    def show(self, names: typing.Iterable[str]=None):
        """Print a formatted version of this table."""
        colpad = 2
        names = names or ()
        columns = {
            name: {'width': len(name)}
            for name in names if name in self.keys
        }
        dashed = {
            name: '-' * column['width']
            for name, column in columns.items()
        }
        for name, column in columns.items():
            values = self.get(name, ())
            for value in values:
                column['width'] = max(column['width'], len(str(value)))
        headers = [
            f"{name:^{2*colpad + column['width']}}"
            for name, column in columns.items()
        ]
        lines = [
            f"{dashed[name]:^{2*colpad + column['width']}}"
            for name, column in columns.items()
        ]
        rows = [
            [
                f"{entry[name]:^{2*colpad + column['width']}}"
                for name, column in columns.items()
            ] for entry in self
        ]
        if headers:
            print(''.join(header for header in headers if header))
        if lines:
            print(''.join(line for line in lines if line))
        for row in rows:
            if row:
                print(''.join(row))

    @property
    def keys(self) -> typing.Set[_KT]:
        """All the keys common to the individual mappings."""
        if self._keys is None:
            all_keys = [list(entry.keys()) for entry in self._entries]
            self._keys = set(all_keys[0]).intersection(*all_keys[1:])
        return self._keys

    def __getitem__(self, key: _KT) -> typing.Tuple[_VT]:
        """Get all the values for a given key if it is common."""
        if key in self.keys:
            values = [entry[key] for entry in self._entries]
            return tuple(values)
        raise TableKeyError(key)

    def get(self, key: _KT, default: typing.Any=None) -> typing.Tuple[_VT]:
        """Get all the values for a given key when available."""
        try:
            return self[key]
        except TableKeyError:
            values = [entry.get(key, default) for entry in self._entries]
            return tuple(values)

    def find(
        self,
        value: _VT,
        unique: bool=False,
    ) -> typing.Union[_ET, typing.List[_ET]]:
        """Find entries with the given value."""
        found = [entry for entry in self._entries if value in entry.values()]
        if not found:
            raise MissingValueError(value)
        if not unique:
            return found
        if len(found) > 1:
            raise AmbiguousValueError(value)
        return found[0]

    def __call__(self, strict: bool=False, **request):
        """Look up an entry by user-requested keys.

        This method will try to return the unique entry in the instance
        collection that contains the given key(s) with the corresponding
        value(s). The iterative search (`strict=False`; default) will iterate
        through the key-value pairs until it either finds a unique entry or runs
        out of pairs. The strict search (`strict=True`) will attempt to find the
        unique entry with all the key-value pairs. Both searches will raise a
        `TableLookupError` if they fail to find a unique entry, or a
        `TableKeyError` if one of the given keys does not exist in all table
        entries. The iterative search will raise an `AmbiguousRequestError` if
        the given key-value pairs are insufficient to determine a unique entry.

        Parameters
        ----------
        strict : bool, default=False
            Fail if any of the given key-value pairs is not in the collection.

        **request : mapping
            Key-value pairs that define the search criteria. Each key must
            appear in all table entries.

            Key-value pairs in which each requested key is a key in every entry
            of the collection. Each requested value may correspond to its
            respective key in zero or more entries for an iterative search, but
            must correspond to its respective key in at least one entry for a
            strict search.

        Returns
        -------
        mapping
            The unique entry containing at least one of the requested key-value
            pairs (iterative search) or all of the requested key-value pairs
            (strict search).

        Raises
        ------
        TableKeyError
            A requested key is not present in every entry.
        
        TableLookupError
            Could not find an entry that matched the requested key-value pairs.

        AmbiguousRequestError
            The given key-value pair is ambiguous. Only applies to iterative
            search.
        """
        subset = [*self._entries]
        for n_checked, pair in enumerate(request.items(), start=1):
            key, value = pair
            if key not in self.keys:
                raise TableKeyError(key)
            subset = [
                entry for entry in subset
                if entry[key] == value
            ]
            if not strict:
                count = self[key].count(value)
                if count > n_checked and len(request) == n_checked:
                    raise AmbiguousRequestError(request)
                if len(subset) == 1:
                    return subset[0]
        if strict and len(subset) == 1:
            return subset[0]
        raise TableLookupError(request)


def distribute(a, b):
    """Distribute `a` and `b` over each other.

    If both `a` and `b` are separable, this function will return their Cartesian
    product. If only `a` or `b` is separable, this function will pair the
    non-separable argument with each element of the separable argument. If
    neither is separable, this function will raise an error.

    See Also
    --------
    `~isseparable`
        Determine if an object is iterable but is not string-like.
    """
    a_separable = isseparable(a)
    b_separable = isseparable(b)
    if not (a_separable or b_separable):
        raise TypeError("At least one argument must be whole")
    if a_separable and b_separable:
        return iter(itertools.product(a, b))
    if not a_separable:
        return iter((a, i) for i in b)
    return iter((i, b) for i in a)


_KT = typing.TypeVar('_KT', bound=str)

_VT = typing.TypeVar('_VT')


class InjectiveTypeError(TypeError):
    """The given mapping contains repeated values."""


class NonInvertibleError(TypeError):
    """The given mapping is not invertible."""


class Bijection(collections.abc.Mapping, typing.Generic[_KT, _VT]):
    """An invertable mapping."""

    def __init__(self, __mapping: typing.Mapping[_KT, _VT]) -> None:
        mapping = dict(__mapping)
        n_keys = len(mapping.keys())
        n_values = len(set(mapping.values()))
        if n_keys > n_values:
            raise InjectiveTypeError(
                f"Cannot initialize {Bijection} from mapping"
                " that is injective but not surjective"
            ) from None
        if n_keys != n_values:
            raise NonInvertibleError(
                f"Cannot initialize {Bijection} from non-invertable mapping"
                f" with {n_keys} keys and {n_values} values"
            ) from None
        self._mapping = mapping

    def __iter__(self) -> typing.Iterator[str]:
        """Called for iter(self)."""
        return iter(self._mapping)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self._mapping)

    def __getitem__(self, key):
        """Look up item by key."""
        return self._mapping[key]

    def invert(self):
        """Invert this mapping."""
        return type(self)({v: k for k, v in self.items()})

    D = typing.TypeVar('D')

    @typing.overload
    def find(self, value: _VT, /) -> _KT: ...

    @typing.overload
    def find(
        self,
        value: _VT,
        default: D,
        /,
    ) -> typing.Union[_KT, D]: ...

    def find(self, value, *args):
        """Get the unique key associated with `value`.

        This method behaves like `dict.pop`, rather than like `dict.get`, in
        that it raises a `KeyError` if `value` is not in this mapping and the
        caller did not provide `default`.

        Parameters
        ----------
        value
            The value of the desired key.
        default : optional
            A value to return if this mapping does not contain `value`.

        Returns
        ------
        key-type
            The key associated with `value`, if `value` exists.
        """
        inverted = self.invert()
        if not args:
            # The caller did not pass a default value.
            return inverted[value]
        # Extract the default value from positional arguments.
        default, *extra = args
        if not extra:
            return inverted.get(value, default)
        # There must not be any extra positional arguments.
        argstr = etc.join([str(x) for x in extra])
        s = '' if len(argstr) == 1 else '(s)'
        raise TypeError(
            f"Got extra positional argument{s} {argstr}"
        ) from None


def length(this):
    """Non-erroring version of `len(this)`.
    
    This function is intended for distinguishing between objects that have
    defined length > 1 and those that do not. It will not distinguish between
    empty iterable objects (e.g., `[]`), which have zero length, and unsized
    objects (e.g., `None`), which have undefined length. Such a distinction may
    be useful when iteratively determining whether or not to subscript a
    sequence or to convert a possibly scalar object into a sequence.
    """
    try:
        n = len(this)
    except TypeError:
        n = 0
    return n


class ObjectRegistry(collections.abc.Mapping, typing.Mapping[_KT, _VT]):
    """A class for associating metadata with abitrary objects."""
    def __init__(
        self,
        base: typing.Mapping[_KT, _VT]=None,
        object_key: str='object',
    ) -> None:
        mapping = dict(base or {})
        self._items = {
            k: dict(v) if isinstance(v, typing.Mapping) else {object_key: v}
            for k, v in mapping.items()
        }
        self._object_key = object_key
        self._init = self._items.copy()
        self._default_key_count = 1

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, key: str) -> bool:
        return key in self._items

    _OT = typing.TypeVar('_OT')

    def register(
        self,
        _obj: _OT=None,
        name: str=None,
        overwrite: bool=False,
        **metadata
    ) -> _OT:
        """Register an object and any associated metadata.

        This function exists to decorate objects. Without any arguments, it will
        log the decorated object in an internal mapping, keyed by the object's
        name. The user may optionally provide key-value pairs of metadata to
        associate with the object.

        Parameters
        ----------
        name : string
            The name to use as this object's key in the internal mapping. The
            default is `None`, which causes this class to create a unique key
            based on the defined name of the object.

        overwrite : bool, default=false
            If true and there is already an object with the key given by `name`,
            overwrite that object. This keyword has no effect if `name` is
            `None`.

        **metadata
            Arbitrary metadata to associate with the decorated object.

        Returns
        -------
        Any
            The decorated object.

        Examples
        --------
        Create an empty object registry, register functions with and without
        metadata, and reset the registry.

        >>> from goats.common.iterables import ObjectRegistry
        >>> from pprint import pprint
        >>> registry = ObjectRegistry()
        >>> @registry.register
        ... def myfunc():
        ...     pass
        ... 
        >>> pprint(registry.mapping)
        {'myfunc': {'object': <function myfunc at 0x7f6097427ee0>}}
        >>> @registry.register(units='cm/s')
        ... def vel():
        ...     pass
        ... 
        >>> pprint(registry.mapping)
        {'myfunc': {'object': <function myfunc at 0x7f6097427ee0>},
        'vel': {'object': <function vel at 0x7f60570fb280>, 'units': 'cm/s'}}
        >>> registry.reset()
        >>> pprint(registry.mapping)
        {}

        Create a registry with an existing `dict` and register a function with
        the same name as an object in the initializing `dict`.

        >>> from goats.common.iterables import ObjectRegistry
        >>> from pprint import pprint
        >>> mymap = {'this': [2, 3]}
        >>> registry = ObjectRegistry(mymap)
        >>> @registry.register
        ... def this():
        ...     pass
        ... 
        >>> pprint(registry.mapping)
        {'this': {'object': [2, 3]},
        'this_1': {'object': <function this at 0x7f46d49961f0>}}

        Create a registry with an existing `dict` and register a function with a
        defined name that is the same as an object in the initializing `dict`,
        but store it under a different name, then repeat the process but
        overwrite the first decorated function.

        >>> from goats.common.iterables import ObjectRegistry
        >>> from pprint import pprint
        >>> mymap = {'this': [2, 3]}
        >>> registry = ObjectRegistry(mymap)
        >>> @registry.register(name='that')
        ... def this():
        ...     pass
        >>> pprint(registry.mapping)
        {'that': {'object': <function this at 0x7f1fab723d30>},
        'this': {'object': [2, 3]}}
        >>> @registry.register(name='that', overwrite=True)
        ... def other():
        ...     pass
        >>> pprint(registry.mapping)
        {'that': {'object': <function other at 0x7f1fab723dc0>},
        'this': {'object': [2, 3]}}
        """
        @functools.wraps(_obj)
        def decorator(obj):
            key = self._get_mapping_key(obj, user=name, overwrite=overwrite)
            self._items[key] = {self._object_key: obj, **metadata}
            return obj
        if _obj is None:
            return decorator
        return decorator(_obj)

    def _get_mapping_key(
        self,
        obj: typing.Any,
        user: str=None,
        overwrite: bool=False
    ) -> str:
        """Get an appropriate key to associate with this object."""
        available = user not in self._items or overwrite
        if user and isinstance(user, typing.Hashable) and available:
            return user
        return self._get_default_key(obj)

    def _get_default_key(self, obj: typing.Any) -> str:
        """Get a default key based on the object's name and existing keys."""
        options = ['__qualname__', '__name__']
        for option in options:
            if hasattr(obj, option):
                proposed = getattr(obj, option)
                if proposed not in self._items:
                    return proposed
                new_default_key = f"{proposed}_{self._default_key_count}"
                self._default_key_count += 1
                return new_default_key

    def reset(self) -> None:
        """Reset the internal mapping to its initial state."""
        self._items = {**self._init}

    def __getitem__(self, key: str) -> typing.Dict[str, typing.Any]:
        """Get an item from the object collection."""
        return self._items[key]

    def copy(self):
        """A shallow copy of this instance."""
        return ObjectRegistry(self._items.copy(), object_key=self._object_key)

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        return f"{self.__class__.__qualname__}({self._items})"


_NT = typing.TypeVar('_NT', bound=numbers.Complex)


class Nearest(typing.NamedTuple):
    """The result of searching an array for a target value."""

    index: int
    value: _NT


def nearest(
    values: typing.Iterable[_NT],
    target: _NT,
    bound: str=None,
) -> Nearest:
    """Find the value in a collection nearest the target value.
    
    Parameters
    ----------
    values : iterable of numbers
        An iterable collection of numbers to compare to the target value. Must
        support conversion to a `numpy.ndarray`.

    target : number
        A single numerical value for which to search in `values`. Must be
        coercible to the type of `values`.

    bound : {None, 'lower', 'upper'}
        The constraint to apply when finding the nearest value:

        - None: no constraint
        - 'lower': ensure that the nearest value is equal to or greater than the
          target value (in other words, the target value is a lower bound for
          the nearest value)
        - 'upper': ensure that the nearest value is equal to or less than the
          target value (in other words, the target value is an upper bound for
          the nearest value)

    Returns
    -------
    Nearest
        A named tuple with `value` and `index` fields, respectively containing
        the value in `values` closest to `target` (given the constraint set by
        `bound`, if any) and the index of `value` in `values`. If the array
        corresponding to `values` is one-dimensional, `index` will be an
        integer; otherwise, it will be a tuple with one entry for each
        dimension.

    Notes
    -----
    This function is based on the top answer to this StackOverflow question:
    https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    However, a lower-voted answer (and the comments) has some suggestions for a
    bisection-based method.
    """

    array = numpy.asarray(values)
    index = numpy.abs(array - target).argmin()
    if bound == 'lower':
        try:
            while array[index] < target:
                index += 1
        except IndexError:
            index = -1
    elif bound == 'upper':
        try:
            while array[index] > target:
                index -= 1
        except IndexError:
            index = 0
    if array.ndim > 1:
        index = numpy.unravel_index(index, array.shape)
    return Nearest(index=index, value=array[index])


class MergeError(Exception):
    """An error occurred while merging iterable objects."""


def merge(these: typing.Iterable, those: typing.Iterable):
    """Merge two iterable containers while respecting order.
    
    Parameters
    ----------
    these, those
        The iterable containers to merge.

    Returns
    -------
    `list`
        A list containing the unique members of the arguments, in the order in
        which they would appear after expanding both arguments.

    Raises
    ------
    `ValueError`
        The arguments contain repeated items in different order.
    """
    x = list(these)
    y = list(those)
    repeated = set(x) & set(y)
    if repeated:
        ab = [i for i in x if i in y]
        ba = [i for i in y if i in x]
        if ab != ba:
            raise MergeError(
                "Repeated entries must appear in the same order"
            ) from None
        s = []
        za = zb = 0
        for v in ab:
            ia = x.index(v)
            ib = y.index(v)
            s.extend(x[za:ia] + y[zb:ib])
            s.append(v)
            za = ia+1
            zb = ib+1
        s.extend(x[za:] + y[zb:])
        return s
    x.extend(y)
    return x


def isiterable(x, /):
    """True if the argument is iterable."""
    try:
        iter(x)
    except TypeError:
        return False
    return True


def size(x, /) -> int:
    """Compute the size of a potentially nested collection.
    
    Parameters
    ----------
    x
        Any non-string iterable container.

    Notes
    -----
    - The non-string restriction on `x` exists to restrict this function to
      array-like objects (e.g., lists of lists). Such objects are considered
      "separable".

    Raises
    ------
    TypeError
        `x` is not iterable or is not separable

    See Also
    --------
    `~isseparable`
    """
    if not isiterable(x):
        raise TypeError(
            f"Cannot compute the size of non-iterable {x}"
        ) from None
    if not isseparable(x):
        raise TypeError(
            f"Argument must be a separable collection, not {type(x)}"
        ) from None
    count = 0
    for y in x:
        if isiterable(y):
            count += size(y)
        else:
            count += 1
    return count


def slice2range(s: slice, /, stop: int=None) -> range:
    """Attempt to convert a `slice` to the equivalent `range`.
    
    Parameters
    ----------
    s : slice
        The `slice` object to convert.

    stop : int, optional
        If given, this function will use the value of `stop` as the (required)
        stop value of the resultant `range` object if the stop value of the
        given `slice` is `None`.

    Returns
    -------
    `range`
        A `range` object built from appropriate start, stop, and step values. If
        the given `slice` doesn't define a start value, this function will use
        0. If the given `slice` doesn't define a step value, this function will
        use 1. See Parameters and Raises for descriptions of behavior for
        different stop values.

    Raises
    ------
    `TypeError`
        Both the stop value of the given `slice` and the value of the `stop`
        keyword parameter are `None`. It is not possible to create a `range`
        object with non-integral stop value.
    """
    if stop is None and s.stop is None:
        raise TypeError(f"Cannot convert {s} to a range.")
    start = s.start or 0 # same effect if s.start == 0
    stop = stop if s.stop is None else s.stop
    step = s.step or 1 # handles invalid case of s.step == 0
    return range(start, stop, step)


def isshapelike(x, /):
    """True if `x` looks like an array shape.
    
    This function will return `True` if `x` is a non-empty iterable object that
    contains only integral members. Otherwise, it will return `False`.
    """
    if not x:
        return False
    return (
        isiterable(x)
        and
        all(isinstance(i, numbers.Integral) for i in x)
    )


