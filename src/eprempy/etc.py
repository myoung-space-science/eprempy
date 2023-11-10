"""
Utilities for the `eprem` package.
"""

import abc
import functools
import inspect
import numbers
import textwrap
import typing

import numpy

# NOTE: This module should not import any modules from the `eprem` package.


T = typing.TypeVar('T')


def strargs(*pos, **kwd) -> str:
    """Format arguments as if explicitly passed."""
    def strfmt(x):
        return repr(x) if isinstance(x, str) else str(x)
    strpos = ', '.join(strfmt(x) for x in pos)
    if not kwd:
        return strpos
    strkwd = ', '.join(f"{k}={strfmt(v)}" for k, v in kwd.items())
    if not pos:
        return strkwd
    return f"{strpos}, {strkwd}"


def underline(text: str):
    """Print underlined text."""
    dashes = '-' * len(text)
    print(f"\n{text}")
    print(dashes)


def doc2help(
    obj: typing.Union[str, typing.Any], /,
    mode: str='summary',
    replacements: typing.Mapping[str, str]=None,
) -> str:
    """Format the target docstring for use as help text.
    
    Parameters
    ----------
    obj
        The target object. If `obj` is a string, this function will directly
        operate on `obj`. If `obj` is an object with a `__doc__` attribute, this
        function will operate on the docstring contained in `obj.__doc__`.

    mode : str, default='sumamry'
        Controls the formatting of the result. In 'summary' mode (the default),
        this function will return the initial (i.e., summary) line of the target
        docstring as written. In 'phrase' mode, this function will return the
        initial line of the docstring in lower case, without a trailing period.
        In 'full' mode, this function will format and return the entire
        docstring.

    replacements : mapping from string to string
        Key-value pairs of strings to replace in the target docstring, where the
        key is the current string and the value is the new string (as in
        ``str.replace``).
    """
    try:
        target = obj if isinstance(obj, str) else str(obj.__doc__)
    except AttributeError:
        raise TypeError(f"Cannot create help text from {obj!r}") from None
    for k, v in (replacements or {}).items():
        target = target.replace(k, v)
    doclines = target.lstrip('\n').split('\n')
    summary = doclines[0]
    if mode == 'full':
        wrapped = textwrap.wrap(
            ' '.join(s.lstrip(' \t') for s in doclines[1:]),
            width=70
        )
        body = '\n'.join(wrapped).lstrip(' ')
        return f"{summary}\n\n{body}"
    if mode == 'phrase':
        return summary[0].lower() + summary[1:].rstrip('.')
    return summary


class InstanceSet(abc.ABCMeta):
    """A metaclass for sets of singletons.

    Using this class as a metaclass will ensure that only one instance of the
    object class exists for a given combination of initializing arguments. Given
    a concrete implementation of `_generate_key`, this metaclass will simply
    return the appropriate existing instance instead of creating a new one.

    See https://refactoring.guru/design-patterns/singleton/python/example
    """

    _instances = {}

    def __call__(self, *args, **kwargs):
        """Ensure that only one instance of the given object exists."""
        key = self._generate_key(*args, **kwargs)
        if key not in self._instances:
            self._instances[key] = super().__call__(*args, **kwargs)
        return self._instances[key]

    @abc.abstractmethod
    def _generate_key(self, *args, **kwargs):
        """Generate a unique instance key.
        
        Concrete implementations of this method must map the given arguments to
        a valid dictionary key, which will be associated with a unique instance.
        """
        raise TypeError(
            "Can't generate unique mapping key"
            f" from {strargs(*args, **kwargs) or 'arguments'}"
        ) from None


def apply(
    methods: typing.Iterable[typing.Callable[..., T]],
    *args,
    **kwargs,
) -> typing.Optional[T]:
    """Apply the given methods until one returns a non-null result."""
    gen = (method(*args, **kwargs) for method in methods)
    if result := next((match for match in gen if match), None):
        return result


def str2repr(__cls: typing.Type[T]):
    """Decorator that provides ``T.__repr__`` based on ``T.__str__``.
    
    Examples
    --------
    The following will define ``Class.__repr__``::

        @str2repr
        class Class:
            def __init__(self, v) -> None:
                self.v = v
            def __str__(self) -> str:
                return f"v={self.v}"

    ```
    >>> c = Class(3)
    >>> print(c)
    3
    >>> c
    Class(v=3)
    ```
    """
    def repr(self: T):
        c = self.__class__
        name = c.__name__
        if '__str__' not in c.__dict__:
            return name
        return f"{name}({self})"
    __cls.__repr__ = repr
    return __cls


def autostr(_obj: typing.Type[T]=None, style: str='default', **kwargs):
    """Decorator that generates `T.__repr__` and `T.__str__` if necessary.
    
    Examples
    --------
    The following will define `Class.__repr__` from `Class.__str__`::

        @autostr
        class Class:
            def __init__(self, v) -> None:
                self.v = v
            def __str__(self) -> str:
                return f"v={self.v}"

    >>> c = Class(3)
    >>> print(c)
    3
    >>> c
    Class(v=3)

    Decorating a class that already defines `__str__` and `__repr__` will not
    modify those methods::

        @autostr
        class Brak:
            def __str__(self) -> str:
                return "Don't touch me."
            def __repr__(self) -> str:
                return "Hey! Don't touch me!"

    >>> b = Brak()
    >>> print(b)
    Don't touch me.
    >>> b
    Hey! Don't touch me!
    """
    @functools.wraps(_obj)
    def wrapper(obj):
        if style == 'numpy':
            return _autostr_numpy(obj, **kwargs)
        if style == 'default':
            return _autostr_default(obj)
    if _obj is None:
        return wrapper
    return wrapper(_obj)


def _autostr_numpy(obj, **kwargs):
    """Helper for `~etc.autostr` in 'numpy' mode."""
    options = {
        'threshold': kwargs.pop('threshold', 4),
        'edgeitems': kwargs.pop('edgeitems', 2),
        'separator': kwargs.pop('separator', ', '),
        'precision': kwargs.pop('precision', 3),
        'floatmode': kwargs.pop('floatmode', 'maxprec_equal'),
    }
    options.update(kwargs)
    def _str(self: T) -> str:
        return numpy.array2string(numpy.array(self), **options)
    prefix = kwargs.pop('prefix', f"{obj.__name__}(")
    suffix = kwargs.pop('suffix', ")")
    def _repr(self: T) -> str:
        content = numpy.array2string(
            numpy.array(self),
            prefix=prefix,
            suffix=suffix,
            **options
        )
        return f"{prefix}{content}{suffix}"
    if '__str__' not in obj.__dict__:
        obj.__str__ = _str
    if '__repr__' not in obj.__dict__:
        obj.__repr__ = _repr
    return obj


def _autostr_default(obj):
    """Helper for `~etc.autostr` in 'default' mode."""
    def _repr(self: T) -> str:
        """An unambiguous representation of this object."""
        c = self.__class__
        name = c.__name__
        if not _defines_str(c):
            return name
        return f"{name}({self})"
    if '__repr__' not in obj.__dict__:
        obj.__repr__ = _repr
    return obj


def _defines_str(this: type):
    """True if `this` type defines a ``__str__`` method.
    
    This function is designed to prevent recursion in `~etc._autostr_default`.
    It checks for ``__str__`` in the ``__dict__`` attribute of `this` type, or
    for a ``__str__`` attribute of `this` type that is not ``object.__str__``. A
    false result indicates to `~etc._autostr_default` that implicitly calling
    `this.__str__` from `_repr` will cause recursion.
    """
    return '__str__' in this.__dict__ or (
        hasattr(this, '__str__')
        and getattr(this, '__str__') != getattr(object, '__str__')
    )


_ST = typing.TypeVar('_ST', bound='Singleton')


class Singleton:
    """A simple base class for creating singletons."""

    _exists = False
    _instance = None

    def __new__(cls: typing.Type[_ST], *args, **kwargs) -> _ST:
        if cls._exists:
            return cls._instance
        new = super(Singleton, cls).__new__(cls)
        cls._exists = True
        cls._instance = new
        return new


class NothingType(Singleton):
    """An object that represents nothing in a variety of ways."""

    def __getitem__(self, index: typing.Any) -> None:
        """Return `None`, regardless of `index`."""
        return None

    def __call__(self, *args, **kwargs) -> None:
        """Return `None`, regardless of input."""
        return None

    def __len__(self) -> int:
        """This object has zero length."""
        return 0

    def __contains__(self, key: str) -> bool:
        """This object contains nothing."""
        return False

    def __iter__(self) -> typing.Iterable:
        """Return an empty iterator.
        
        Thanks to https://stackoverflow.com/a/36658865/4739101 for this one.
        """
        yield from ()

    def __next__(self):
        """There is always nothing left."""
        raise StopIteration

    def __bool__(self) -> bool:
        """This object is always false."""
        return False

    def __repr__(self) -> str:
        """This object knows that it is nothing."""
        return "Nothing"


Nothing = NothingType()
"""A unique object that represents nothing."""


class SentinelInitError(Exception):
    """Attempt to directly instantiate a new sentinel object."""


class SentinelValueError(ValueError):
    """Value error while creating a sentinel object."""


_sentinels = {}
"""Internal mapping of singleton key-value pairs (a.k.a sentinels)."""


def _sentinel_init(f):
    """Decorator for `~_SentinelType.__init__`.
    
    The core purpose of this decorator function is to force
    `~_SentinelType.__init__` to unconditionally raise `NotImplementedError`. It
    does so by consuming all user arguments, which would cause the runtime
    environment to raise a `ValueError` before `~_SentinelType.__init__` could
    raise `NotImplementedError`.
    """
    exception = SentinelInitError
    def _parse_args(*args, **kwargs):
        """Create a string to represent the user arguments.
        
        If this function detects that `*args` and `**kwargs` represent valid
        arguments to `~sentinel`, it will return a string representing the
        corresponding arguments. Otherwise, it will return `None`. In the former
        case, `_make_errmsg` will create a message that includes the appropriate
        function call. In the latter case, `_make_errmsg` will create a generic
        message that defers to the `~sentinel` documentation.
        """
        if len(args) == 2 and not kwargs:
            name = args[0]
            if isinstance(name, str):
                return f"{name!r}, {args[1]}"
        if len(args) == 1 and list(kwargs) == ['value']:
            name = args[0]
            if isinstance(name, str):
                return f"{name!r}, value={kwargs['value']}"
        if not args and list(kwargs) == ['name', 'value']:
            name = kwargs['name']
            if isinstance(name, str):
                return f"name={name!r}, value={kwargs['value']}"
    def _make_errmsg(*args, **kwargs):
        """Create an appropriate error message for the given arguments."""
        strfunc = f"{__name__}.sentinel"
        if strargs := _parse_args(*args, **kwargs):
            return f"Please call {strfunc}({strargs}) instead."
        return f"Please see {strfunc} for more information."
    expected = NotImplementedError
    def method(self, *args, **kwargs):
        """Wrapper method for `__init__`."""
        errmsg = _make_errmsg(*args, **kwargs)
        try:
            f(self)
        except expected as err:
            raise exception(
                f"Cannot directly instantiate {type(self)}. {errmsg}"
            ) from err
        raise RuntimeError(
            f"Failed to catch {expected}"
            f" during attempt to instantiate {type(self)}"
        ) from None
    return method


class _SentinelType(typing.Generic[T]):
    """Factory class for singleton key-value pairs."""

    _name: str
    _value: T

    @classmethod
    def _create(cls, name: str, value: T):
        """Pseudo-private instantiation method."""
        if value in _sentinels:
            return _sentinels[value]
        instance = cls.__new__(cls)
        instance._name = name
        instance._value = value
        _sentinels[name] = instance
        return instance

    @_sentinel_init
    def __init__(self) -> None:
        """It is not possible to instantiate this class.
        
        Please use the `~sentinel` factory function.
        """
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        """Called for self == other."""
        if not isinstance(other, _SentinelType):
            return self._value == other
        return self is other

    def __bool__(self):
        """Called for bool(self)."""
        if self._value in (None, False):
            return False
        return True

    def __hash__(self):
        """Called for hash(self)."""
        return hash(self._value)

    def __repr__(self) -> str:
        """The canonical name of this sentinel object."""
        return self._name


def sentinel(name: str, value: T) -> _SentinelType:
    """Create a new sentinel object.
    
    This function provides the public interface for creating new sentinel
    objects, which are essentially singleton key-value pairs.

    Parameters
    ----------
    name : string
        The name of the new sentinel object. This should be the same as the name
        of the variable to which it is bound (e.g., `X = sentinel('X', -1)`).
    value
        The value that the new object will represent.

    Returns
    -------
    `~_SentinelType`
    """
    if isinstance(value, _SentinelType):
        raise SentinelValueError(
            f"Sentinel object {__name__}.{value!r} already exists"
        ) from None
    return _SentinelType._create(name, value)


PASS = sentinel('PASS', True)
"""Sentinel object equivalent to `True`."""

NULL = sentinel('NULL', None)
"""Sentinel object equivalent to `None`."""

FAIL = sentinel('FAIL', False)
"""Sentinel object equivalent to `False`."""


def isnull(this: typing.Any) -> bool:
    """True if `this` is empty but not if it's 0.

    This function allows the calling code to programmatically test for objects
    that are logically ``False`` except for numbers equivalent to 0.
    """
    if isinstance(this, numbers.Number):
        return False
    size = getattr(this, 'size', None)
    if size is not None:
        return size == 0
    try:
        result = not bool(this)
    except ValueError:
        result = all((isnull(i) for i in this))
    return result


def join(x: typing.Iterable[str], c: str='and', /, quoted: bool=False):
    """Join strings, with a conjunction before the final item.
    
    Parameters
    ----------
    x : iterable of strings
        The strings to join. This function will convert `x` into a `list`.
    
    c : string
        The conjunction to insert before the final item, if `x` contains more
        than one string.

    quoted : bool, default=False
        If true, quote each string in `x`.

    Notes
    -----
    - This function will insert the conjunction as given. It is the user's
      responsibility to pass an appropriate argument.
    - This function implements the `quoted` option by calling `repr` on each
      string in `x`.
    """
    f = repr if quoted else str
    y = list(x)
    if len(y) == 1:
        return f(y[0])
    if len(y) == 2:
        return f"{f(y[0])} {c} {f(y[1])}"
    substr = ', '.join(f(i) for i in y[:-1])
    return f"{substr}, {c} {f(y[-1])}"


def allisinstance(types, *targets):
    """True if every target object is an instance of the given type(s).
    
    Parameters
    ----------
    types : type or tuple of types
        The types against which to check the target objects.

    targets
        The objects to check.

    Returns
    -------
    `bool`

    Raises
    ------
    `TypeError`
        The user provided no objects to check.

    See Also
    --------
    `~container.hastype`
        True if an iterable object contains certain types.

    Notes
    -----
    - The calling signature is reversed from that of `isinstance(x, types)` in
      order to accommodate a variable number of target objects.
    - Calling this function with a single target object, `x`, is equivalent to
      calling `isinstance(x, types)`.
    """
    if not targets:
        raise TypeError("Missing object arguments") from None
    return all(isinstance(target, types) for target in targets)


V = typing.TypeVar('V')


class classproperty(typing.Generic[T, V]):
    """A read-only property derived from a `classmethod`.

    Notes
    -----
    - This implementation is based on Django's `classproperty`:
      https://docs.djangoproject.com/en/3.0/_modules/django/utils/decorators/
    - See other suggestions at
        - https://stackoverflow.com/a/13624858/4739101
        - https://stackoverflow.com/a/5191224
    - See https://docs.python.org/3/howto/descriptor.html#properties for a
      pure-Python implementation of `property`.
    - See notes at https://docs.python.org/3/howto/descriptor.html#class-methods
      for additional notes about chaining `classmethod` with other decorators.
    """

    def __init__(
        self,
        method: typing.Callable[[typing.Type[T]], V],
    ) -> None:
        self.fget = classmethod(method)

    def __get__(self, obj: T, objtype: typing.Type[T]=None):
        t = type(obj) if objtype is None else objtype
        return self.fget.__get__(t, t)()

    def getter(self, method: typing.Callable[[typing.Type[T]], V]):
        self.fget = classmethod(method)
        return self


def isproperty(this: object) -> bool:
    """True if `this` is a Python instance property.
    
    This function is designed for use as a predicate with `inspect.getmembers`.
    """
    return inspect.isdatadescriptor(this) and isinstance(this, property)


A = typing.TypeVar('A')
B = typing.TypeVar('B')
T = typing.TypeVar('T')

def widest(a: A, b: B, base: typing.Optional[typing.Type[T]]=None):
    """Determine the widest type between `a` and `b`."""
    if base is None:
        if type(a) == type(b):
            return type(a)
        if issubclass(type(a), type(b)):
            return type(a)
        if issubclass(type(b), type(a)):
            return type(b)
        raise ValueError(
            f"Cannot determine appropriate type from {type(a)} and {type(b)}"
        ) from None
    if not (issubclass(type(a), base) and issubclass(type(b), base)):
        raise TypeError(
            f"{base} is not a common base type of {type(a)} and {type(b)}"
        ) from None
    if isinstance(a, base) and isinstance(b, base):
        if type(a) == type(b):
            return type(a)
        if issubclass(type(a), type(b)):
            return type(a)
        if issubclass(type(b), type(a)):
            return type(b)
        return base
    if isinstance(a, base):
        return type(a)
    if isinstance(b, base):
        return type(b)
    raise ValueError(
        f"Cannot determine appropriate type from {type(a)} and {type(b)}"
    ) from None


