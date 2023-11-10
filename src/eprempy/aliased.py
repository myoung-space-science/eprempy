import abc
import collections
import collections.abc
import typing

from . import container


_KT = typing.TypeVar('_KT')
_AT = typing.TypeVar('_AT')
_VT = typing.TypeVar('_VT')


class Group(collections.abc.Set, typing.Generic[_KT]):
    """A group of associated aliases."""

    __slots__ = ('_aliases')

    _builtin = (tuple, list, set)

    @classmethod
    def supports(cls, key: _KT):
        """True if `key` can instantiate this class."""
        try:
            cls(key)
        except TypeError:
            return False
        return True

    def __init__(self, *a: typing.Union[_KT, typing.Iterable[_KT]]) -> None:
        if not a:
            raise TypeError("At least one alias is required") from None
        self._aliases = self._from_iterable(a)

    @classmethod
    def _from_iterable(
        cls,
        it: typing.Tuple[typing.Union[_KT, typing.Iterable[_KT]]],
    ) -> typing.Set[_KT]:
        return container.unwrap(it, newtype=set)

    def __iter__(self):
        return iter(self._aliases)

    def __len__(self) -> int:
        return len(self._aliases)

    def __contains__(self, key: str) -> bool:
        return key in self._aliases

    def __hash__(self) -> int:
        """Compute the hash of the underlying key set."""
        return hash(tuple(self._aliases))

    def __bool__(self) -> bool:
        """Called for bool(self)."""
        # NOTE: The truth value of a Group is equal to whether or not it has at
        # least one alias. Since it is currently not possible to instantiate a
        # Group with zero aliases, this should always return True.
        return bool(self._aliases)

    def _implement(operator):
        def method(self: 'Group', other):
            return operator(self, Group(other))
        def wrapper(self, other):
            result = method(self, other)
            if isinstance(result, typing.Iterable):
                return type(self)(result)
            return result
        return wrapper

    __eq__ = _implement(collections.abc.Set.__eq__)
    __and__ = _implement(collections.abc.Set.__and__)
    isdisjoint = _implement(collections.abc.Set.isdisjoint)
    __or__ = _implement(collections.abc.Set.__or__)
    __sub__ = _implement(collections.abc.Set.__sub__)
    __rsub__ = _implement(collections.abc.Set.__rsub__)
    __xor__ = _implement(collections.abc.Set.__xor__)

    def __str__(self) -> str:
        """A simplified representation of this instance."""
        return self._display_items(separator=' = ')

    def __repr__(self) -> str:
        """An unambiguous representation of this instance."""
        items = self._display_items(separator=', ')
        module = f"{self.__module__.replace('eprempy.', '')}."
        name = self.__class__.__qualname__
        return f"{module}{name}({items})"

    def _display_items(self, separator: str=', '):
        """Build a collection of strings for printing."""
        items = {f"{k!r}" for k in self._aliases}
        return separator.join(items)


GroupsType = typing.TypeVar('GroupsType', bound='Groups')


class Groups(collections.abc.MutableSet, typing.Generic[_KT]):
    """A collection of unique groups of associated members."""

    def __init__(
        self,
        *keys: typing.Union[_KT, typing.Iterable[_KT]],
    ) -> None:
        """
        Parameters
        ----------
        keys
            Zero or more groups of associated objects.
        """
        self._groups = [Group(key) for key in keys]

    @classmethod
    def _from_iterable(cls, it):
        """Overloaded to match constructor signature."""
        return cls(*tuple(it))

    @property
    def flat(self):
        """All current aliases, in a single list."""
        return [key for group in self._groups for key in group]

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self._groups)

    def __iter__(self):
        """Called for iter(self)."""
        return iter(self._groups)

    def __contains__(self, __x: _KT) -> bool:
        """Called for __x in self."""
        return self.get(__x) is not None

    def update(
        self: GroupsType,
        *others: typing.Union[_KT, typing.Iterable[_KT], GroupsType]
    ) -> None:
        """Merge groups from `others` into these groups."""
        if not others:
            return
        self._groups = self._merge(*others)

    def merge(
        self: GroupsType,
        *others: typing.Union[_KT, typing.Iterable[_KT], GroupsType]
    ) -> GroupsType:
        """Create a new instance with merged groups."""
        return type(self)(*self._merge(*others))

    def _merge(self, *others):
        """Combine this instance's groups with other groups."""
        these = self._groups.copy()
        for this in others:
            groups = this if isinstance(this, Groups) else [this]
            for group in groups:
                if found := self._search(group):
                    these.remove(found)
                    these.append(found | group)
                else:
                    these.append(group)
        return these

    def _search(self, group: typing.Iterable[_KT]):
        """Search for a member of `group` that is in this instance."""
        for member in group:
            if found := self.get(member):
                return found

    def add(self, __x: typing.Iterable[_KT]) -> None:
        """Add `__x` to the existing groups."""
        for i in __x:
            if i in self.flat:
                raise ValueError(
                    f"Cannot add {__x}: {i} already exists in a group"
                ) from None
        self._groups.append(Group(__x))

    def discard(self, __x: _KT) -> None:
        """Remove the group containing `__x`."""
        if found := self.get(__x):
            self._groups.remove(found)

    def __getitem__(self, __x: _KT):
        """Get the group containing `__x`."""
        s = str(__x)
        m = Group(__x)
        alias = (k for k in self._groups if s in k or m == k)
        try:
            found = next(alias)
        except StopIteration as err:
            raise KeyError(
                f"No group containing {__x!r}"
            ) from err
        return found

    DefaultType = typing.TypeVar('DefaultType')

    def get(self, __x: _KT, default: typing.Optional[DefaultType]=None):
        """Get the group containing `__x`, if possible.
        
        This method will sequentially check for a one of the following cases:
            - one of the internal mapping keys contains the given key
            - the given key is equal to one of the internal mapping keys

        If it finds a match, it will immediately return that group (i.e.,
        without checking other keys). If not, it will return `default`.
        """
        s = str(__x)
        m = Group(__x)
        alias = (k for k in self._groups if s in k or m == k)
        return next(alias, default)

    def without(self, *keys: typing.Union[_KT, Group[_KT]]):
        """Create a new keymap after removing `keys`."""
        subset = [
            group
            for group in self._groups
            if (
                # none of the keys is in this group
                all(key not in group for key in keys)
                and
                # this group is not one of the keys
                group not in keys
            )
        ]
        return type(self)(*subset)

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        module = f"{self.__module__.replace('eprempy.', '')}."
        name = self.__class__.__qualname__
        items = ', '.join(str(group) for group in self._groups)
        return f"{module}{name}({items})"


def keysfrom(
    mapping: typing.Mapping[_KT, typing.Mapping[_KT, _VT]],
    aliases: typing.Optional[typing.Union[_KT, Groups[_KT]]]=None,
) -> typing.List[Group[_KT]]:
    """Extract keys for use in an aliased mapping.
    
    Parameters
    ----------
    mapping
        Same as for `~aliased.Mapping.__init__`.

    aliases
        Same as for `~aliased.Mapping.__init__`.

    Examples
    --------
    >>> mapping = {
    ...     'a': {'aliases': ('A', 'a0'), 'n': 1, 'm': 'foo'},
    ...     'b': {'aliases': 'B', 'n': -4},
    ... }
    >>> keys = keysfrom(mapping)
    >>> keys
    [MappingKey('a | A | a0'), MappingKey('B | b')]
    """
    if isinstance(mapping, Mapping):
        return mapping.keys(aliased=True)
    if aliases is None:
        return [Group(k) for k in mapping.keys()]
    if isinstance(aliases, Groups):
        return [
            Group(k) | aliases.get(k, ())
            for k in mapping.keys()
        ]
    return [
        Group(k) | Group(v.get(aliases, ()))
        for k, v in mapping.items()
    ]


def _build_mapping(
    mapping: typing.Mapping=None,
    aliases: typing.Union[str, Groups[str]]=None,
) -> dict:
    """Build the internal `dict` for an `~aliased.Mapping`."""
    # Is it empty?
    if not mapping:
        return {}
    # Did the user provide explicit aliases?
    if aliases:
        return _build_from_key(mapping, aliases=aliases)
    # Does the mapping contain implicit aliases?
    if any(
        isinstance(group, typing.Mapping) and 'aliases' in group
        for group in mapping.values()
    ): return _build_from_key(mapping, aliases='aliases')
    # Does it have the form {<aliased key>: <value>}?
    if all(Group.supports(key) for key in mapping):
        return _build_from_aliases(mapping)
    # Is it a built-in dictionary?
    if isinstance(mapping, dict):
        return mapping.copy()


def _build_from_aliases(
    mapping: typing.Mapping[_KT, _VT],
) -> typing.Dict[Group, _VT]:
    """Build a `dict` that maps aliased keys to user values."""
    out = {}
    for key, value in mapping.items():
        try:
            aliased_key = next(k for k in out if key in k)
        except StopIteration:
            aliased_key = Group(key)
        out[aliased_key] = value
    return out


def _build_from_key(
    mapping: typing.Mapping[str, typing.Mapping[str, typing.Any]],
    aliases: typing.Union[str, Groups[str]]=None,
) -> typing.Dict[Group, _VT]:
    """Build a `dict` with aliased keys taken from interior mappings.
    
    Parameters
    ----------
    mapping
        An object that maps string keys to interior mappings of strings to
        any type.

    aliases
        Same as for `~aliased.Mapping.__init__`.

    Examples
    --------
    Create aliased mappings from a user dictionary with the default alias
    key::

    >>> mapping = {
    ...     'a': {'aliases': ('A', 'a0'), 'n': 1, 'm': 'foo'},
    ...     'b': {'aliases': 'B', 'n': -4},
    ... }
    >>> amap = aliased.Mapping(mapping)
    >>> amap
    aliased.Mapping('a0 | A | a': {'n': 1, 'm': 'foo'}, 'b | B': {'n': -4})
    >>> amap['a']
    {'n': 1, 'm': 'foo'}

    Create aliased mappings from a user dictionary, swapping the alias key::

    >>> mapping = {
    ...     'a': {'foo': 'A', 'bar': 'a0'},
    ...     'b': {'foo': 'B', 'bar': 'b0'},
    ... }
    >>> amap = aliased.Mapping(mapping, aliases='foo')
    >>> amap
    aliased.Mapping('A | a': a0, 'b | B': b0)
    >>> amap['a']
    'a0'
    >>> amap = aliased.Mapping(mapping, aliases='bar')
    >>> amap
    aliased.Mapping('a0 | a': A, 'b | b0': B)
    >>> amap['a']
    'A'
    """
    keys = keysfrom(mapping, aliases=aliases)
    values = [
        {k: v for k, v in group.items() if k != aliases}
        for group in mapping.values()
    ] if aliases and isinstance(aliases, str) else mapping.values()
    return dict(zip(keys, values))


@typing.runtime_checkable
class _MappingProtocol(typing.Protocol[_KT, _VT]):
    """Protocol for aliased mappings."""

    __slots__ = ()

    @property
    @abc.abstractmethod
    def as_dict(self) -> typing.Dict[_KT, _VT]:
        pass

    @abc.abstractmethod
    def _flat_keys(self) -> typing.KeysView[_KT]:
        pass

    @abc.abstractmethod
    def __getitem__(self, __k: _KT) -> _VT:
        pass


class MappingView(collections.abc.MappingView, typing.Generic[_KT, _VT]):
    """Base class for views of aliased mappings."""

    __slots__ = ('_mapping', '_keys')

    def __init__(
        self,
        mapping: _MappingProtocol[_KT, _VT],
        aliased: bool=False,
    ) -> None:
        super().__init__(mapping)
        aliases = mapping.as_dict.keys()
        self._keys = aliases if aliased else mapping._flat_keys()
        self._mapping = mapping

    def __len__(self):
        """Called for len(self)."""
        return len(self._keys)

    def __str__(self):
        """A simplified representation of this object."""
        return str(list(self))

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        module = f"{self.__module__.replace('eprempy.', '')}."
        name = self.__class__.__qualname__
        return f"{module}{name}({self})"


class KeysView(MappingView[_KT, _VT], collections.abc.KeysView):
    """A view on the keys of an aliased mapping."""

    def __iter__(self):
        """Iterate over aliased mapping keys."""
        yield from self._keys


class ValuesView(MappingView[_KT, _VT], collections.abc.ValuesView):
    """A view on the values of an aliased mapping."""

    def __iter__(self):
        """Iterate over aliased mapping values."""
        for key in self._keys:
            yield self._mapping[key]


class ItemsView(MappingView[_KT, _VT], collections.abc.ItemsView):
    """A view on the key-value pairs of an aliased mapping."""

    def __iter__(self):
        """Iterate over aliased mapping items."""
        for key in self._keys:
            yield (key, self._mapping[key])


_MT = typing.TypeVar('_MT', bound='Mapping')


class Mapping(collections.abc.Mapping, typing.Generic[_KT, _VT]):
    """A mapping class that supports aliased keys.
    
    Examples
    --------
    Create an instance from a standard `dict` with strings or tuples of strings
    as keys.

    >>> mapping = {'a': 1, ('b', 'B'): 2, ('c', 'C', 'c0'): -9}
    >>> amap = aliased.Mapping(mapping)
    >>> amap
    Mapping('a': 1, 'b | B': 2, 'c | C | c0': -9)

    The caller may access an individual item by any one (but only one) of its
    valid aliases.

    >>> amap['a']
    1
    >>> amap['b']
    2
    >>> amap['B']
    2
    >>> amap[('b', 'B')]
    ...
    KeyError: ('b', 'B')

    Aliased items are identical.

    >>> amap['b'] is amap['B']
    True

    The representation of keys, values, and items reflect the internal grouping
    by alias, but iterating over each produces de-aliased members. This behavior
    naturally supports loops and comprehensions, since access is only valid for
    individual items.

    >>> amap.keys()
    AliasedKeys(['a', 'b | B', 'c | C | c0'])
    >>> amap.values()
    AliasedValues([1, 2, -9])
    >>> amap.items()
    AliasedItems([('a', 1), ('b | B', 2), ('c | C | c0', -9)])
    >>> list(amap.keys())
    ['a', 'b', 'B', 'c', 'C', 'c0']
    >>> list(amap.values())
    [1, 2, 2, -9, -9, -9]
    >>> list(amap.items())
    [('a', 1), ('b', 2), ('B', 2), ('c', -9), ('C', -9), ('c0', -9)]
    >>> for k, v in amap.items():
    ...     print(k, amap[k], v)
    ... 
    a 1 1
    b 2 2
    B 2 2
    c -9 -9
    C -9 -9
    c0 -9 -9

    It is always possible to access the equivalent de-aliased `dict`.

    >>> amap.flat
    {'a': 1, 'b': 2, 'B': 2, 'c': -9, 'C': -9, 'c0': -9}

    Updates and deletions apply to all associated aliases.

    >>> amap['c'] = 5.6
    >>> list(amap.items())
    [('a', 1), ('b', 2), ('B', 2), ('c', 5.6), ('C', 5.6), ('c0', 5.6)]
    >>> del amap['c']
    >>> list(amap.items())
    [('a', 1), ('b', 2), ('B', 2)]

    Users may access all aliases for a given key via the `alias` method.
    Attempting to register an alias will raise a `KeyError` if it is already an
    alias for a different key.

    >>> amap.alias('b')
    MappingKey('B')
    >>> amap.alias('b', include=True)
    MappingKey('b | B')
    >>> amap.alias(b='my B')
    >>> amap.alias('b')
    MappingKey('B | my B')
    >>> amap
    Mapping('a': 1, 'b | my B | B': 2)
    >>> amap.alias(a='b')
    ...
    KeyError: "'b' is already an alias for '(B, my B)'"

    Notes
    -----
    The length of this object, as well as its keys, values, and items, is equal
    to the number of valid aliases it contains. This is consistent with the
    many-to-one nature of the mapping despite the fact that it internally stores
    aliases and values in a one-to-one mapping.
    """

    @typing.overload
    def __init__(
        self,
        mapping: typing.Mapping[typing.Union[_KT, typing.Tuple[_KT]], _VT],
    ) -> None: ...

    @typing.overload
    def __init__(
        self,
        mapping: typing.Mapping[_KT, typing.Mapping[_AT, _VT]],
        aliases: typing.Optional[_AT]=None,
    ) -> None: ...

    @typing.overload
    def __init__(
        self,
        mapping: typing.Mapping[_KT, _VT],
        aliases: typing.Optional[Groups[_KT]]=None,
    ) -> None: ...

    @typing.overload
    def __init__(
        self: _MT,
        mapping: typing.Mapping[_KT, _VT],
        aliases: typing.Optional[_MT]=None,
    ) -> None: ...

    def __init__(self, mapping=None, aliases=None) -> None:
        """Initialize this instance.
        
        Parameters
        ----------
        mapping : mapping, default=None
            An object that maps strings or iterables of strings to values of any
            type. If the keys are iterables of strings, grouped keys will
            represent aliases for each other. Omitting this argument will
            produce an empty mapping.

        aliases : string or `~Mapping` or `~Groups`, default='aliases'
            Either a string that points to values in `mapping` to use as
            aliases, an instance of `~aliased.Groups` that maps keys in
            `mapping` to the values to use as their aliases, or an instance of
            this class. The first case assumes that the values of `mapping` are
            themselves mappings. These values will not appear in the aliased
            mapping values.
        """
        self.as_dict = self._build_dict(mapping, aliases)
        self._flat_dict = {alias: k for k in self.as_dict for alias in k}

    def _build_dict(self, mapping, aliases):
        """Build the equivalent `dict` attribute."""
        if isinstance(mapping, Mapping):
            return dict(mapping.items(aliased=True))
        if isinstance(aliases, Mapping):
            return _build_mapping(
                mapping=mapping,
                aliases=Groups(*aliases.keys(aliased=True)),
            )
        if isinstance(aliases, typing.Mapping):
            groups = [
                [key, new] if isinstance(new, str) else [key, *new]
                for key, new in aliases.items()
            ]
            return _build_mapping(
                mapping=mapping,
                aliases=Groups(*groups),
            )
        return _build_mapping(mapping=mapping, aliases=aliases)

    def _flat_keys(self) -> typing.KeysView[str]:
        """Define a flat list of all the keys in this mapping."""
        flattened = [key for keys in self.as_dict.keys() for key in keys]
        return collections.abc.KeysView(flattened)

    @property
    def flat(self) -> typing.Dict[str, _VT]:
        """Expand aliased items into a standard dictionary."""
        return {key: self[key] for key in self._flat_keys()}

    def __contains__(self, __o) -> bool:
        """True if `__o` is a key in this mapping.
        
        Overloaded to avoid going through `__getitem__`.
        """
        return self._resolve(__o) is not None

    def __iter__(self) -> typing.Iterator:
        yield from self._flat_keys()

    def __len__(self) -> int:
        return len(self._flat_keys())

    def __getitem__(self, key: typing.Union[str, Group]) -> _VT:
        """Look up a value by one of its keys."""
        if resolved := self._resolve(key):
            return self.as_dict[resolved]
        raise KeyError(
            f"The key {str(key)!r}"
            " does not correspond to a known name or alias"
        ) from None

    def _resolve(self, key: typing.Union[Group, typing.Any]):
        """Resolve `key` into an existing or new aliased key."""
        if isinstance(key, Group):
            return self._look_up_key(key)
        return self._flat_dict.get(key)

    def _look_up_key(self, target: Group):
        """Find the aliased key equivalent to `target`.
        
        Notes
        -----
        Checking ``key in self.as_dict`` doesn't always work because `dict`
        look-up will first compare the key's hash value to those of existing
        keys before comparing the key itself. This may fail in the first stage
        due to the fact that `MappingKey.__hash__` uses `tuple.__hash__`, which
        depends on order, despite the fact that the second stage should pass
        because `MappingKey.__eq__` does not depend on order. See
        https://stackoverflow.com/q/327311/4739101.
        """
        try:
            found = next(key for key in self.as_dict if key == target)
        except StopIteration:
            return
        else:
            return found

    def squeeze(self, strict: bool=False):
        """Reduce singleton interior mappings, if possible.
        
        If this aliased mapping contains a single key-value pair for every
        aliased key, this method will replace each interior mapping with its
        values.

        Parameters
        ----------
        strict : bool, default=False
            If true, raise an exception when attempting to remove singleton
            interior mappings with different keys.
        """
        interior = tuple(self.as_dict.values())
        if all(len(mapping) == 1 for mapping in interior):
            if strict:
                errmsg = (
                    "Can't squeeze interior mappings with different keys"
                    " when strict == True"
                )
                k0 = tuple(interior[0].keys())[0]
                for mapping in interior[1:]:
                    k = tuple(mapping.keys())[0]
                    if k != k0:
                        raise TypeError(errmsg) from None
            new = {
                k: tuple(v.values())[0] for k, v in self.as_dict.items()
            }
            self.as_dict = new.copy()
        return self

    @classmethod
    def fromkeys(
        cls: typing.Type[_MT],
        __iterable: typing.Iterable[_KT],
        key: str='aliases',
        value: _VT=None,
    ) -> _MT:
        """Create an aliased mapping based on another mapping's keys.

        Parameters
        ----------
        __iterable
            A mapping capable of initializing `~aliases.Mapping`, an iterable
            capable of initializing `~aliases.Groups`, or an instance of
            `~aliases.Groups`.

        key : string
            Same as for `~aliases.Mapping.__init__`. Ignored of `__iterable` is
            an `~aliased.Groups` or a non-mapping iterable.

        value : any
            The fill value to use for all items.

        Returns
        -------
        aliased mapping
            A new instance of this class, with aliased keys taken from the
            user-provided mapping and each value set to the given value.

        Examples
        --------
        Create an aliased mapping with keys taken from a pre-defined dictionary
        and all values set to -1.0

        >>> mapping = {
        ...     'a': {'aliases': ('A', 'a0'), 'n': 1, 'm': 'foo'},
        ...     'b': {'aliases': 'B', 'n': -4},
        ...     'c': {'n': 42},
        ... }
        >>> amap = aliased.Mapping.fromkeys(mapping, value=-1.0)
        >>> amap
        aliased.Mapping('a0 | a | A': -1.0, 'B | b': -1.0, 'c': -1.0)
        >>> keys = [('a', 'A', 'a0'), ('B', 'b'), 'c']
        >>> amap = aliased.Mapping.fromkeys(keys, value=-1.0)
        >>> amap
        aliased.Mapping('a0 | a | A': -1.0, 'B | b': -1.0, 'c': -1.0)
        >>> keys = aliased.Groups(*keys)
        >>> amap = aliased.Mapping.fromkeys(keys, value=-1.0)
        >>> amap
        aliased.Mapping('a0 | a | A': -1.0, 'B | b': -1.0, 'c': -1.0)
        """
        if (
            isinstance(__iterable, Groups)
            or not isinstance(__iterable, typing.Mapping)
        ): return cls({k: value for k in __iterable})
        keys = keysfrom(__iterable, aliases=key)
        d = {k: value for k in keys}
        return cls(d)

    def alias(self, key: str, *, include=False):
        """Get the alias for an existing key.
        
        Parameters
        ----------
        key : string
            An existing key for which to return aliases.

        include : bool, default=False
            If true, include the current key in the returned aliases.
        """
        if include:
            return self._resolve(key)
        return self._resolve(key) - [key]

    def __eq__(self, other: typing.Mapping) -> bool:
        """Define equality between this and another object."""
        if not isinstance(other, typing.Mapping):
            return NotImplemented
        if isinstance(other, Mapping):
            return self.items() == other.items()
        return dict(self.items()) == dict(other.items())

    def __or__(self, other):
        """Merge this aliased mapping with `other`."""
        if isinstance(other, Mapping):
            others = other.items(aliased=True)
        elif isinstance(other, typing.Mapping):
            others = other.items()
        else:
            return NotImplemented
        items = dict((*self.items(aliased=True), *others))
        return type(self)(items)

    def __str__(self) -> str:
        """A simplified representation of this instance."""
        return ', '.join(
            f"{k}: {self[k]!r}" for k in self.keys(aliased=True)
        )

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        module = f"{self.__module__.replace('eprempy.', '')}."
        name = self.__class__.__qualname__
        return f"{module}{name}({self})"

    def keys(self, aliased: bool=False):
        """A view on this instance's keys."""
        return KeysView(self, aliased=aliased)

    def values(self, aliased: bool=False):
        """A view on this instance's values."""
        return ValuesView(self, aliased=aliased)

    def items(self, aliased: bool=False):
        """A view on this instance's key-value pairs."""
        return ItemsView(self, aliased=aliased)

    def copy(self):
        """Create a shallow copy of this instance."""
        return type(self)(self.as_dict)


class MutableMapping(Mapping, collections.abc.MutableMapping):
    """A mutable version of `Mapping`.
    
    Parameters
    ----------
    mapping : mapping
        An object that maps strings or iterables of strings to values of any
        type.

    Examples
    --------
    These examples build on the examples shown in `Mapping`.

    >>> mutable = iterables.MutableMapping(aliased)

    Updates and deletions apply to all associated aliases.

    >>> mutable['c'] = 5.6
    >>> list(mutable.items())
    [('a', 1), ('b', 2), ('B', 2), ('c', 5.6), ('C', 5.6), ('c0', 5.6)]
    >>> del mutable['c']
    >>> list(mutable.items())
    [('a', 1), ('b', 2), ('B', 2)]

    Users may access all aliases for a given key, or register new ones, via the
    `alias` method. Attempting to register an alias will raise a `KeyError` if
    it is already an alias for a different key.

    >>> mutable.alias('b')
    MappingKey('B')
    >>> mutable.alias('b', include=True)
    MappingKey('b | B')
    >>> mutable.alias(b='my B')
    >>> mutable.alias('b')
    MappingKey('B | my B')
    >>> mutable
    Mapping('a': 1, 'b | my B | B': 2)
    >>> mutable.alias(a='b')
    ...
    KeyError: "'b' is already an alias for '(B, my B)'"

    Notes
    -----
    See note on lengths at `~Mapping`.
    """
    def __init__(self, mapping=None, aliases=None) -> None:
        super().__init__(mapping, aliases)
        self._groups = {}

    def __getitem__(self, key: typing.Union[str, Group]) -> _VT:
        if key in self._groups:
            return tuple(
                super(MutableMapping, self).__getitem__(k)
                for k in self._groups[key]
            )
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: _VT):
        """Assign a value to `key` and its aliases."""
        resolved = self._resolve(key) or Group(key)
        self.as_dict[resolved] = value
        self._refresh()

    def __delitem__(self, key: str):
        """Remove the item corresponding to `key`."""
        resolved = self._resolve(key)
        if not resolved:
            raise KeyError(f"'{key!r}' is not a known name or alias.") from None
        del self.as_dict[resolved]
        self._refresh()

    def _refresh(self):
        """Perform common tasks after setting or deleting an item."""
        self._flat_dict = {
            alias: key for key in self.as_dict for alias in key
        }

    def alias(self, key: str, *aliases: str, include=False):
        """Get or set the alias(es) for an existing key.
        
        Parameters
        ----------
        key : string
            An existing key for which to return aliases.

        aliases : iterable of string
            Zero or more aliases to associate with `key`, if they are not
            already in use.

        include : bool, default=False
            If true, include the current key in the returned aliases.
        """
        if not aliases:
            return super().alias(key, include=include)
        for alias in (a for a in aliases if a != key):
            if alias in self._flat_keys():
                current = super().alias(key)
                this = ", ".join(str(a) for a in current)
                if len(current) > 1:
                    this = f'({this})'
                raise KeyError(
                    f"'{key}' is already an alias for {this!r}"
                ) from None
            updated = self._resolve(key) | alias
            self.as_dict[updated] = self[key]
            del self[key]

    def group(self, name: str, *keys: str):
        """View or create a groups of aliased items.
        
        Parameters
        ----------
        name : string
            The name of the group. When creating a new group, `name` cannot be
            an existing key.
        *keys : string
            Zero or more existing keys to associate with `name`. If there are no
            keys and there is an existing group for `name` , this method will
            return the keys in that group.

        Examples
        --------
        Create a simple instance of this class:

        >>> base = {'a': 1, 'b': 2, 'c': 3}
        >>> mapping = aliased.MutableMapping(base)

        The keys are the same as for a ``dict``:

        >>> sorted(mapping)
        ['a', 'b', 'c']

        Create a new group:

        >>> mapping.group('G', 'a', 'b')

        The mapping keys do not change:

        >>> sorted(mapping)
        ['a', 'b', 'c']

        Accessing the group key returns the associated values:

        >>> tuple(mapping['G'])
        (1, 2)

        You can check the original keys associated with the group key:

        >>> mapping.group('G')
        ('a', 'b')

        Attempting to access an unknown group key raises ``KeyError``:

        >>> mapping.group('H')
        Traceback (most recent call last):
        ...
        KeyError: "No key group called 'H'"
        """
        if name in self:
            raise ValueError(
                f"Cannot assign group to existing key {name!r}"
            ) from None
        if not keys:
            if name not in self._groups:
                raise KeyError(f"No key group called {name!r}") from None
            return self._groups[name]
        self._groups[name] = keys

    def freeze(self, groups: bool=False):
        """Generate a new immutable mapping from this instance.
        
        Parameters
        ----------
        groups : boolean, default=false
            If true, map existing groups to new items in the result. The default
            behavior is to ignore groups when creating the new mapping.
        """
        if not groups:
            return Mapping(self)
        grouped = {k: self[k] for k in self._groups}
        return Mapping({**self, **grouped})


class NameMap(collections.abc.Mapping):
    """A mapping from aliases to canonical names.
    
    Notes
    -----
    See note on lengths at `~Mapping`.
    """

    AliasDefinitions = typing.TypeVar('AliasDefinitions')
    AliasDefinitions = typing.Union[
        typing.Iterable[typing.Iterable[str]],
        typing.Mapping[str, typing.Iterable[str]],
        typing.Mapping[str, typing.Mapping[str, typing.Iterable[str]]],
    ]

    AliasReferences = typing.TypeVar('AliasReferences')
    AliasReferences = typing.Union[
        typing.Iterable[str],
        typing.Mapping[str, typing.Any],
    ]

    def __init__(
        self,
        defs: AliasDefinitions,
        refs: AliasReferences=None,
        key: str='aliases',
    ) -> None:
        names = self._get_names(defs, refs)
        self._mapping = self._build_mapping(names, defs, key)
        self._init = {'refs': refs, 'defs': defs, 'key': key}

    def __len__(self):
        """Called for len(self)."""
        return len(self._mapping.keys())

    def __iter__(self):
        """Called for iter(self)."""
        return iter(self._mapping.keys())

    RT = typing.TypeVar('RT')

    RT = typing.Union[
        typing.Iterable[str],
        typing.Iterable[typing.Iterable[str]],
    ]

    def _get_names(
        self,
        defs: AliasDefinitions,
        refs: AliasReferences=None,
    ) -> RT:
        """Create an iterable of canonical names, if possible."""
        if isinstance(refs, typing.Mapping):
            return refs.keys()
        if isinstance(refs, typing.Iterable):
            return refs
        if isinstance(defs, typing.Mapping):
            return defs.keys()
        raise TypeError(
            f"Can't create name map from {defs!r} and {refs!r}"
        ) from None

    def _build_mapping(self, names, aliases, key):
        """Build the internal mapping from aliases to canonical names.

        This method first creates an identity map of canonical
        names (i.e., `name` -> `name`), with which it spawns a trivial aliased
        mapping. It then determines the appropriate aliases for each canonical
        name and updates the aliased-mapping keys. The result is a mapping from
        one or more aliases to a canonical name. In case there are no aliases
        associated with a canonical name, its aliased key will simply contain
        itself.
        """
        identity = {name: name for name in names}
        namemap = MutableMapping(identity)
        updates = self._get_aliases(names, aliases, key)
        for current, new in updates.items():
            namemap.alias(current, *new)
        return Mapping(namemap)

    def _get_aliases(self, names, these: AliasDefinitions, key):
        """Determine the appropriate aliases for each canonical name."""
        # Mapping <: Iterable, so we need to check Mapping first.
        if isinstance(these, typing.Mapping):
            # There are two allowed types of Mapping:
            # 1) Mapping[str, Mapping[str, Iterable[str]]]
            # 2) Mapping[str, Iterable[str]]
            
            # Make sure the keys are all strings. NOTE: I'm not sure that this
            # catches cases in which `these` values are mappings. Need to add a
            # test case.
            if any(k for k in these if not isinstance(k, str)):
                raise TypeError("All aliases must be strings") from None
            # Again, we need to check Mapping values before Iterable values.
            return {
                k: self._remove(k, v.get(key, ()))
                if isinstance(v, typing.Mapping)
                else self._remove(k, v)
                for k, v in these.items()
            }
        # Alias definitions are in a non-mapping iterable. We may want to
        # further check that each member of `aliases` is itself an iterable of
        # strings.
        only_iterables = all(isinstance(d, typing.Iterable) for d in these)
        if isinstance(these, typing.Iterable) and only_iterables:
            return {k: tuple(v) for v in these for k in names if k in v}
        return {}

    def _remove(self, name: str, aliases: typing.Iterable):
        """Remove `name` from `aliases`."""
        w = (aliases,) if isinstance(aliases, str) else aliases
        return tuple(i for i in w if i != name)

    def __getitem__(self, key: str):
        """Get the canonical name for `key`."""
        if key in self._mapping:
            return self._mapping[key]
        raise KeyError(key)

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return self._display_items(separator='\n')

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        items = self._display_items(separator='; ')
        return f"{self.__class__.__qualname__}({items})"

    def _display_items(self, separator: str=', '):
        """Build a collection of 'key: value' strings."""
        items = {
            f"{str(k)!r}: {str(v)!r}"
            for k, v in self._mapping.items(aliased=True)
        }
        return separator.join(items)

    def keys(self, aliased: bool=False):
        """A view on this object's aliased keys."""
        return Mapping.keys(self._mapping, aliased=aliased)

    def values(self, aliased: bool=False):
        """A view on this object's aliased values."""
        return Mapping.values(self._mapping, aliased=aliased)

    def items(self, aliased: bool=False):
        """A view on this object's aliased key-value pairs."""
        return Mapping.items(self._mapping, aliased=aliased)

    def copy(self):
        """Make a shallow copy of this object."""
        return type(self)(**self._init)


