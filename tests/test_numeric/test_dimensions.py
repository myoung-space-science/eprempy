import itertools

import pytest

from eprempy import numeric


def test_dimensions_object():
    """Make sure dimensions behave as expected in operations."""
    assert len(numeric.dimensions()) == 0
    names = ['a', 'b', 'c']
    for i, name in enumerate(names, start=1):
        subset = names[:i]
        dimensions = numeric.dimensions(*subset)
        assert len(dimensions) == i
        assert all(name in dimensions for name in subset)
        assert dimensions[i-1] == name


def test_dimensions_factory():
    """Test various ways to initialize a dimensions attribute."""
    default = numeric.dimensions(3)
    assert len(default) == 3
    assert list(default) == ['x0', 'x1', 'x2']
    names = ['a', 'b', 'c']
    assert len(numeric.dimensions(names)) == 3
    assert len(numeric.dimensions(*names)) == 3
    assert len(numeric.dimensions([names])) == 3
    invalid = [
        [1, 2, 3],
        [[1], [2], [3]],
        [['a'], ['b'], ['c']],
    ]
    for case in invalid:
        with pytest.raises(TypeError):
            numeric.dimensions(*case)


def test_dimensions_unique():
    """All dimensions should be unique."""
    cases = {
        ('a', 'b', 'b'): ('a', 'b'),
        (('a', 'b', 'b'),): ('a', 'b'),
        ('a', 'a', 'b'): ('a', 'b'),
        (('a', 'a', 'b'),): ('a', 'b'),
        ('a', 'a', 'a'): ('a',),
        (('a', 'a', 'a'),): ('a',),
    }
    for args, true in cases.items():
        this = numeric.dimensions(*args)
        that = numeric.dimensions(*true)
        assert this == that


def test_dimensions_comparisons():
    """Test binary comparison operations on dimensions."""
    xy = numeric.dimensions('x', 'y')
    # binary comparisons follow set-like logic
    assert xy < ['x', 'y', 'z']
    assert xy <= ['x', 'y', 'z']
    assert xy <= ['x', 'y']
    assert xy >= ['x', 'y']
    assert xy >= ['x']
    assert xy > ['x']
    # order matters for equality
    assert xy == ['x', 'y']
    assert xy != ['y', 'x']


def test_dimensions_or():
    """Test the ability to merge unique dimensions in order."""
    xy = numeric.dimensions('x', 'y')
    yz = numeric.dimensions('y', 'z')
    zw = numeric.dimensions('z', 'w')
    xyz = numeric.dimensions('x', 'y', 'z')
    xyzw = numeric.dimensions('x', 'y', 'z', 'w')
    xwzy = numeric.dimensions('x', 'w', 'z', 'y')
    valid = [
        (xy, xy, ['x', 'y']),
        (xy, yz, ['x', 'y', 'z']),
        (yz, xy, ['x', 'y', 'z']),
        (xy, zw, ['x', 'y', 'z', 'w']),
        (zw, xy, ['z', 'w', 'x', 'y']),
        (yz, zw, ['y', 'z', 'w']),
        (xyzw, xy, ['x', 'y', 'z', 'w']),
        (xy, xyzw, ['x', 'y', 'z', 'w']),
    ]
    for a, b, r in valid:
        assert a | b == numeric.dimensions(*r)
        assert a | list(b) == numeric.dimensions(*r)
        assert list(a) | b == numeric.dimensions(*r)
    assert xy | 'z' == xyz
    assert (xy | 'z') | 'w' == xyzw
    assert xy | yz | 'w' == xyzw
    invalid = [
        (xyzw, xwzy),
        (zw, xwzy),
        (xwzy, zw),
    ]
    for a, b in invalid:
        with pytest.raises(ValueError):
            a | b


def test_dimensions_replace():
    """Test the ability to replace a dimension."""
    old = numeric.dimensions('a', 'b')
    new = old.replace('b', 'c')
    assert isinstance(new, numeric.Dimensions)
    assert old == ['a', 'b']
    assert new == ['a', 'c']


def test_dimensions_sub():
    """Test the ability to remove a named dimension."""
    names = ['a', 'b', 'c']
    old = numeric.dimensions(*names)
    for name in names:
        new = old - name
        expected = [n for n in names if n != name]
        assert new == numeric.dimensions(*expected)
    new = (old - names[0]) - names[1]
    assert new == numeric.dimensions(names[2])
    with pytest.raises(TypeError):
        names[0] - old


def test_dimensions_and():
    """Test the ability to extract common dimensions in order."""
    a = numeric.dimensions('x', 'y', 'z')
    b = numeric.dimensions('y', 'z', 'w')
    expected = numeric.dimensions('y', 'z')
    assert a & b == expected
    assert a & list(b) == expected
    assert list(a) & b == expected


def test_dimensions_insert():
    """Test the ability to extract common dimensions in order."""
    old = numeric.dimensions('x', 'y', 'z')
    assert old.insert('a', 1) == numeric.dimensions('x', 'a', 'y', 'z')
    assert old.insert('a', 2) == numeric.dimensions('x', 'y', 'a', 'z')


def test_dimensions_copy():
    """Test the ability to create a copy of dimensions."""
    names = ['a', 'b', 'c']
    old = numeric.dimensions(*names)
    new = old.copy()
    assert new == old
    assert new is not old


def test_dimensions_permute():
    """Test the ability to permute the order of dimensions."""
    names = ['a', 'b', 'c']
    old = numeric.dimensions(*names)
    for permutation in itertools.permutations(names):
        order = [names.index(i) for i in permutation]
        expected = numeric.dimensions(permutation)
        assert old.permute(order) == expected
        assert old.permute(*order) == expected
        assert old.permute(order=order) == expected
    trivial = (0, 1, 2)
    with pytest.raises(TypeError):
        old.permute(*trivial, order=trivial)
    with pytest.raises(TypeError):
        old.permute(trivial, order=trivial)
    with pytest.raises(TypeError):
        old.permute()
    with pytest.raises(ValueError):
        old.permute(2, 1)
    with pytest.raises(ValueError):
        old.permute(4, 3, 2, 1)
    with pytest.raises(ValueError):
        old.permute(names)
    with pytest.raises(ValueError):
        old.permute(*names)
    with pytest.raises(ValueError):
        old.permute(order=names)


