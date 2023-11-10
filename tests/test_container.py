import typing

import numpy
import pytest

from eprempy import container


def test_unique():
    """Test the function that extracts unique items while preserving order."""
    cases = {
        'a': ['a'],
        (1, 2): [1, 2],
        'ab': ['a', 'b'],
        ('a', 'b'): ['a', 'b'],
        ('a', 'b', 'a'): ['a', 'b'],
        ('a', 'b', 'a', 'c'): ['a', 'b', 'c'],
        ('a', 'b', 'b', 'a', 'c'): ['a', 'b', 'c'],
        (('a', 'b', 'b', 'a', 'c'),): ['a', 'b', 'c'],
        ((1,),): [1],
        ((1, 2),): [1, 2],
        (1, 2): [1, 2],
        (('a', 'a'), ('b', 'b')): [('a', 'a'), ('b', 'b')],
    }
    for items, expected in cases.items():
        assert list(container.unique(*items)) == expected
    with pytest.raises(TypeError):
        container.unique(1)


def test_unique_strict():
    """Test use of the `strict` keyword argument to `unique`."""
    result = container.unique(['a', 'b', 'a'], strict=True)
    expected = [['a', 'b', 'a']]
    assert result == expected


def test_unwrap():
    """Test the function that removes certain outer sequence types."""
    cases = [[3], (3,), [[3]], [(3,)], ([3],), ((3,),)]
    for case in cases:
        assert container.unwrap(case) == 3
    for case in [[3], [[3]], (3,), [(3,)]]:
        assert container.unwrap(case, newtype=list) == [3]
        assert container.unwrap(case, newtype=tuple) == (3,)
        assert isinstance(
            container.unwrap(case, newtype=iter),
            typing.Iterator
        )
    for case in [[3, 4], (3, 4), [(3, 4)], ([3, 4])]:
        assert container.unwrap(case, newtype=list) == [3, 4]
        assert container.unwrap(case, newtype=tuple) == (3, 4)


@pytest.mark.xfail
def test_wrap():
    """Test the function that wraps an object in a list."""
    assert False


def test_isseparable():
    """Test the function that identifies non-string iterables."""
    separables = [[1, 2], (1, 2), range(1, 3)]
    for arg in separables:
        assert container.isseparable(arg)
    nonseparables = ['a', '1, 2', 1, 1.0, slice(None), slice(1)]
    for arg in nonseparables:
        assert not container.isseparable(arg)


def test_hastype():
    """Test the function that checks for compound type matches."""
    # 1) all identical to `isinstance(...)`
    assert container.hastype(1, int)
    assert container.hastype('s', str)
    assert container.hastype([1, 2], list)
    # 2) targets have declared type and are wrapped in a `list`
    assert container.hastype([1, 2], int, list)
    # 3) same as case 2, but no declared wrapper
    assert not container.hastype([1, 2], int)
    # 4) same as case 2, but declared wrapper is not `list`
    assert not container.hastype([1, 2], int, tuple)
    # 5) similar to case 2, but one target has undeclared type
    assert not container.hastype([1, 2.0], int, list, strict=True)
    # 6) non-strict versions of 5
    assert container.hastype([1, 2.0], int, list, strict=False)
    assert container.hastype([1, '2.0'], int, list, strict=False)
    # 7) similar to cases 5 & 6, with consistent types
    assert container.hastype([1, 2.0], (int, float), list, strict=False)
    assert container.hastype([1, 2.0], (int, float), list, strict=True)
    # 8) variations on case 7 in which `float` is interpreted as a wrapper type
    #    (may lead to subtle bugs in user code)
    assert not container.hastype([1, 2.0], int, float, list, strict=True)
    assert container.hastype([1, 2.0], int, float, list)
    # *) indices tested in test_variable.py::test_variable_getitem
    indices = [
        slice(None),
        Ellipsis,
        (0, 0),
        (0, slice(None)),
        (slice(None), 0),
        (slice(None), slice(0, 1, None)),
    ]
    types = (int, slice, type(...))
    for index in indices:
        assert container.hastype(index, types, tuple, strict=True)
    assert not container.hastype('hello', types, strict=True)


def test_find_first():
    """Test the function that finds the first instance of a type."""
    assert container.find_first(str, 1, 'a', 'b') == 'a'
    assert container.find_first(int, 1, 'a', 2) == 1
    assert container.find_first(list, 1, 'a', [2]) == [2]


def test_wrapper():
    """Test the type that defines a collection of distinct members."""
    value = 2
    wrapped = container.Wrapper(value)
    assert len(wrapped) == 1
    assert value in wrapped
    assert list(wrapped) == [2]
    values = [1, 2]
    wrapped = container.Wrapper(values)
    assert len(wrapped) == len(values)
    assert all(value in wrapped for value in values)
    assert list(wrapped) == list(values)
    separables = [
        container.Wrapper(None),
        container.Wrapper([]),
        container.Wrapper(()),
    ]
    for wrapped in separables:
        assert len(wrapped) == 0
        assert not list(wrapped)
    string = '1, 2'
    wrapped = container.Wrapper(string)
    assert len(wrapped) == 1
    assert string in wrapped
    assert string != wrapped
    assert list(wrapped) == [string]


@pytest.fixture
def standard_entries():
    """A collection of well-behaved entries for a Table instance."""
    return [
        {'name': 'Gary', 'nickname': 'Gare-bear', 'species': 'cat'},
        {'name': 'Pickles', 'nickname': 'Pick', 'species': 'cat'},
        {'name': 'Ramon', 'nickname': 'Ro-ro', 'species': 'dog'},
        {'name': 'Frances', 'nickname': 'Frank', 'species': 'turtle'},
    ]


@pytest.fixture
def extra_key():
    """A collection of entries in which one has an extra key."""
    return [
        {'lower': 'a', 'upper': 'A'},
        {'lower': 'b', 'upper': 'B'},
        {'lower': 'c', 'upper': 'C', 'example': 'car'},
    ]


def test_table_lookup(standard_entries: list):
    """Test the object that supports multi-key look-up."""
    table = container.Table(standard_entries)
    gary = table(name='Gary')
    assert gary['nickname'] == 'Gare-bear'
    assert gary['species'] == 'cat'
    this = table(nickname='Ro-ro')
    assert this['name'] == 'Ramon'
    assert this['species'] == 'dog'
    with pytest.raises(container.TableLookupError):
        table(name='Simone')
    with pytest.raises(container.AmbiguousRequestError):
        table(species='cat')
    okay = table(species='cat', name='Pickles')
    assert okay['nickname'] == 'Pick'
    with pytest.raises(container.TableLookupError):
        table(species='dog', name='Gary', strict=True)
    with pytest.raises(container.TableLookupError):
        table(nickname='Yrag', species='dog', name='Gary', strict=True)


def test_table_errors(
    standard_entries: list,
    extra_key: list,
) -> None:
    """Regression test for `Table` error messages.

    This is separate from other tests in case we want to assert that `Table`
    raised a particular exception but we don't care what the actual message is.
    """
    standard = container.Table(standard_entries)
    extra = container.Table(extra_key)

    message = "Table has no common key 'example'"
    with pytest.raises(container.TableKeyError, match=message):
        standard(example='bird')
    with pytest.raises(container.TableKeyError, match=message):
        standard(example='bird', strict=True)
    with pytest.raises(container.TableKeyError, match=message):
        extra(example='car')
    message = "Table has no entry with species=dog and name=Gary"
    with pytest.raises(container.TableLookupError, match=message):
        standard(species='dog', name='Gary', strict=True)
    message = (
        "Table has no entry with"
        " nickname=Yrag, species=cat, and name=Gary"
    )
    with pytest.raises(container.TableLookupError, match=message):
        standard(nickname='Yrag', species='cat', name='Gary', strict=True)
    message = "Table has no entry with name=Simone"
    with pytest.raises(container.TableLookupError, match=message):
        standard(name='Simone')
    message = "The search criterion 'species=cat' is ambiguous"
    with pytest.raises(container.AmbiguousRequestError, match=message):
        standard(species='cat')


def test_table_modes(standard_entries: list):
    """Test the search modes available to Table."""
    def permute(d: dict, n: int=0) -> dict:
        """Permute the dict by `n` (anti-cyclic for n < 0)."""
        if n == 0:
            return d
        keys = list(d.keys())
        if n < 0:
            l = len(keys)
            perm = keys[l+n::-1] + keys[:l+n:-1]
        else:
            perm = keys[n:] + keys[:n]
        return {k: d[k] for k in perm}

    table = container.Table(standard_entries)
    valid = {'name': 'Gary', 'nickname': 'Gare-bear', 'species': 'cat'}
    permutations = []
    length = len(valid)
    for n in range(length):
        permutations.extend([permute(valid, n), permute(valid, n-length)])
    for request in permutations:
        entry = table(**request)
        assert entry['name'] == 'Gary'
        assert entry['nickname'] == 'Gare-bear'
        assert entry['species'] == 'cat'
    for request in permutations[:4]:
        entry = table(**{**request, **{'species': 'dog'}})
        assert entry['name'] == 'Gary'
        assert entry['nickname'] == 'Gare-bear'
        assert entry['species'] == 'cat'
    for request in permutations[4:]:
        entry = table(**{**request, **{'species': 'dog'}})
        assert entry['name'] == 'Ramon'
        assert entry['nickname'] == 'Ro-ro'
        assert entry['species'] == 'dog'
    with pytest.raises(container.TableLookupError):
        table(name='Gary', nickname='Gare-bear', species='dog', strict=True)


def test_table_getitem(extra_key: list):
    """Make sure we can get values of a common key via [] syntax."""
    table = container.Table(extra_key)
    subset = [entry['lower'] for entry in extra_key]
    assert table['lower'] == tuple(subset)
    with pytest.raises(container.TableKeyError):
        table['example']


def test_table_get(extra_key: list):
    """Make sure we can get value of any key, or a default value."""
    table = container.Table(extra_key)
    subset = [entry.get('example') for entry in extra_key]
    assert table.get('example') == tuple(subset)
    subset = [entry.get('example', -1) for entry in extra_key]
    assert table.get('example', -1) == tuple(subset)


def test_table_find(standard_entries: list):
    """Test table look-up by value."""
    table = container.Table(standard_entries)
    expected = {'name': 'Pickles', 'nickname': 'Pick', 'species': 'cat'}
    assert table.find('Pickles') == [expected]
    assert table.find('Pickles', unique=True) == expected
    expected = [
        {'name': 'Gary', 'nickname': 'Gare-bear', 'species': 'cat'},
        {'name': 'Pickles', 'nickname': 'Pick', 'species': 'cat'},
    ]
    assert table.find('cat') == expected
    with pytest.raises(container.AmbiguousValueError):
        table.find('cat', unique=True)
    with pytest.raises(container.MissingValueError):
        table.find('pidgeon')


def test_distribute():
    """Test the function that distributes one object over another."""
    expected = [('a', 1), ('a', 2), ('b', 1), ('b', 2)]
    assert list(container.distribute(['a', 'b'], [1, 2])) == expected
    expected = [('a', 1), ('a', 2)]
    assert list(container.distribute('a', [1, 2])) == expected
    expected = [('a', 1), ('b', 1)]
    assert list(container.distribute(['a', 'b'], 1)) == expected


def test_bijection():
    """Test the class the represents a bijective (one-to-one) mapping."""
    mapping = {'a': 1, 'b': 2, 'c': 3}
    forward = container.Bijection(mapping)
    assert forward['a'] == 1
    assert forward['b'] == 2
    assert forward['c'] == 3
    inverse = forward.invert()
    assert inverse[1] == 'a'
    assert inverse[2] == 'b'
    assert inverse[3] == 'c'
    for k, v in forward.items():
        assert forward.find(v) == inverse[v]
        assert forward[k] == inverse.find(k)
        with pytest.raises(KeyError):
            forward.find(k)
        with pytest.raises(KeyError):
            inverse.find(v)
    assert forward.find('bad', 'okay') == 'okay'
    assert inverse.find('bad', 'okay') == 'okay'
    with pytest.raises(KeyError):
        forward.find('bad')
    with pytest.raises(KeyError):
        inverse.find('bad')
    with pytest.raises(TypeError):
        forward.find('a', default=-1)
    with pytest.raises(TypeError):
        forward.find('a', -1, 99)


def test_bijection_errors():
    test = {
        'a': 1,
        'b': 2,
        'c': 3,
    }
    invalid = {
        **test,
        'd': test['a'],
    }
    with pytest.raises(container.InjectiveTypeError):
        container.Bijection(invalid)


def test_length():
    """Test the non-erroring measure of length."""
    cases = {
        1: 0,
        (1,): 1,
        (1, 1): 2,
    }
    for arg, expected in cases.items():
        assert container.length(arg) == expected


def test_object_registry():
    """Test the class that holds objects with metadata."""
    registry = container.ObjectRegistry({'this': [2, 3]})
    assert registry['this']['object'] == [2, 3]
    @registry.register(name='func', color='blue')
    def func():
        pass
    assert registry['func']['object'] == func
    assert registry['func']['color'] == 'blue'
    assert len(registry) == 2
    assert 'func' in registry
    assert sorted(registry) == sorted(['this', 'func'])


def test_nearest():
    values = [0.1, 0.2, 0.3]
    basic = {
        0.11: (0, 0.1),
        0.15: (0, 0.1),
        0.20: (1, 0.2),
    }
    for target, (index, value) in basic.items():
        found = container.nearest(values, target)
        assert found.index == index
        assert found.value == value
    for target in [0.21, 0.25, 0.29]:
        found = container.nearest(values, target, bound='lower')
        assert found.index == 2
        assert found.value == 0.3
        found = container.nearest(values, target, bound='upper')
        assert found.index == 1
        assert found.value == 0.2
    values = numpy.arange(3.0 * 4.0 * 5.0).reshape(3, 4, 5)
    found = container.nearest(values, 32.9)
    assert found.index == (1, 2, 3)
    assert found.value == 33.0


def test_merge():
    """Test the order-preserving merge function."""
    valid = [
        [['a', 'b'], ['x', 'y'], ['a', 'b', 'x', 'y']],
        [['x', 'y', 'z'], ['x', 'y', 'z'], ['x', 'y', 'z']],
        [['x', 'y', 'z'], ['x', 'y'], ['x', 'y', 'z']],
        [['x', 'y', 'z'], ['y', 'z'], ['x', 'y', 'z']],
        [['x', 'y', 'z'], ['x', 'z'], ['x', 'y', 'z']],
        [['y', 'z'], ['x', 'y', 'z'], ['x', 'y', 'z']],
        [['y', 'z'], ['z', 'w'], ['y', 'z', 'w']],
        [['x', 'y', 'z'], ['y', 'z', 'w'], ['x', 'y', 'z', 'w']],
        [
            ['x', 'y', 'z', 'w', 'r'],
            ['a', 'x', 'b', 'c', 'y', 'w'],
            ['a', 'x', 'b', 'c', 'y', 'z', 'w', 'r'],
        ],
        [
            ['a', 'x', 'b', 't', 'y', 'c', 'z'],
            ['a', 'q', 'x', 'q', 'p', 'c', 'r'],
            ['a', 'q', 'x', 'b', 't', 'y', 'q', 'p', 'c', 'z', 'r'],
        ],
        [
            ['a', 'q', 'x', 'q', 'p', 'c', 'r'],
            ['a', 'x', 'b', 't', 'y', 'c', 'z'],
            ['a', 'q', 'x', 'q', 'p', 'b', 't', 'y', 'c', 'r', 'z'],
        ],
    ]
    for these, those, expected in valid:
        assert container.merge(these, those) == expected
    invalid = [
        [['a', 'b', 'c'], ['a', 'c', 'b']],
        [['a', 'c', 'b'], ['a', 'b', 'c']],
    ]
    for these, those in invalid:
        with pytest.raises(container.MergeError):
            container.merge(these, those)


def test_isiterable():
    """Test the function that checks for iterable input."""
    class Iterable:
        def __iter__(self):
            yield from ()
    class NotIterable:
        def __iter__(self):
            raise TypeError
    cases = [
        (1, False),
        ('1', True),
        ([1], True),
        ((1,), True),
        ([], True),
        ((), True),
        ({}, True),
        (set(), True),
        (None, False),
        (Iterable(), True),
        (NotIterable(), False),
    ]
    for (x, truth) in cases:
        assert container.isiterable(x) == truth
    # NOTE: These are intended to ensure that calling `isiterable(arg)` doesn't
    # modify `arg` (e.g., by exhausting an iterator).
    x = [1, 2]
    container.isiterable(x)
    assert x == [1, 2]
    y = iter(x)
    container.isiterable(y)
    assert list(y) == [1, 2]
    z = (i for i in x)
    container.isiterable(z)
    assert list(z) == [1, 2]


def test_size():
    """Test the function that computes the size of a nested collection."""
    valid = [
        ([], 0),
        ([1], 1),
        ([1, 2], 2),
        ([[1], [2]], 2),
        ([[1, 2], [3, 4]], 4),
        ([1, 2, 3, 4], 4),
        ([[1, 2, 3, 4]], 4),
    ]
    for (x, n) in valid:
        assert container.size(x) == n
    error = [
        1,
        None,
        '1',
        '[1]',
    ]
    for x in error:
        with pytest.raises(TypeError):
            container.size(x)


def test_slice2range():
    """Test the function that converts a slice to a range."""
    assert container.slice2range(slice(3)) == range(0, 3, 1)
    assert container.slice2range(slice(3, 9)) == range(3, 9, 1)
    assert container.slice2range(slice(3, 9, 2)) == range(3, 9, 2)
    assert container.slice2range(slice(None), stop=4) == range(4)
    with pytest.raises(TypeError):
        container.slice2range(slice(None))


def test_isshapelike():
    """Test the function that checks for potential array shapes."""
    valid = [
        ([0, 1, 2, 3], True),
        ((0, 1, 2, 3), True),
        (range(4), True),
        ([], False),
        ((), False),
        (None, False),
        ('shape', False),
    ]
    for arg, truth in valid:
        assert container.isshapelike(arg) == truth
