import numbers

import numpy
import pytest

from eprempy import etc


def test_strargs():
    """Test the argument-formating function."""
    pos = [-1, 'b']
    kwd = {'c': 1, 'd': 'D'}
    assert etc.strargs(*pos) == "-1, 'b'"
    assert etc.strargs(*pos, **kwd) == "-1, 'b', c=1, d='D'"
    assert etc.strargs(**kwd) == "c=1, d='D'"


def test_str2repr():
    """Test the decorator that defines __repr__ based on __str__."""
    @etc.str2repr
    class A:
        def __init__(self, x) -> None:
            self.x = x
    class B(A):
        def __str__(self) -> str:
            return str(self.x)
    a = A(2)
    assert str(a) == 'A'
    assert repr(a) == 'A'
    b = B(2)
    assert str(b) == '2'
    assert repr(b) == 'B(2)'


def test_autostr_default():
    """Test the decorator that generates missing __str__ and __repr__."""
    @etc.autostr
    class A:
        def __init__(self, name: str) -> None:
            self.name = name
    class B(A):
        def __str__(self) -> str:
            return f"name={self.name!r}"
    class C(A):
        def __repr__(self) -> str:
            return f"value={self.name!r}"
    class D(A):
        def __str__(self) -> str:
            return f"str is {self.name!r}"
        def __repr__(self) -> str:
            return f"repr is {self.name!r}"
    class V(B):
        pass
    a = A('two')
    assert str(a) == 'A'
    assert repr(a) == 'A'
    b = B('two')
    assert str(b) == "name='two'"
    assert repr(b) == "B(name='two')"
    c = C('two')
    assert str(c) == "value='two'"
    assert repr(c) == "value='two'"
    d = D('two')
    assert str(d) == "str is 'two'"
    assert repr(d) == "repr is 'two'"
    v = V('two')
    assert str(v) == str(b)
    assert repr(v) == repr(b).replace('B', 'V')


def test_autostr_numpy():
    """Test the decorator that generates missing __str__ and __repr__."""
    # Test the basic numpy style.
    @etc.autostr(style='numpy')
    class A:
        def __init__(self, x) -> None:
            self.x = numpy.array(x)
        def __array__(self, *args, **kwargs):
            return numpy.asarray(self.x, *args, **kwargs)
    a = A([2.1, -3.9])
    assert  str(a) ==   "[ 2.1, -3.9]"
    assert repr(a) == "A([ 2.1, -3.9])"
    # Try an option the make sure it goes through.
    @etc.autostr(style='numpy', suppress_small=True)
    class B:
        def __init__(self, x) -> None:
            self.x = numpy.array(x)
        def __array__(self, *args, **kwargs):
            return numpy.asarray(self.x, *args, **kwargs)
    b = B([2.1, -3.9, 1e-16])
    assert  str(b) ==   "[ 2.1, -3.9,  0.0]"
    assert repr(b) == "B([ 2.1, -3.9,  0.0])"


def test_nothing():
    """Test the object that represents nothing."""
    assert not etc.Nothing
    assert len(etc.Nothing) == 0
    assert etc.Nothing['at all'] is None
    assert etc.Nothing(to_see='here') is None
    assert 'something' not in etc.Nothing
    for _ in etc.Nothing:
        assert False
    with pytest.raises(StopIteration):
        next(etc.Nothing)
    this = etc.NothingType()
    assert this is etc.Nothing


def test_sentinel_type():
    """Test arbitrary sentinel creation and known error cases."""
    x = etc.sentinel('x', 1)
    assert str(x) == 'x'
    assert x == 1
    for y in (etc.PASS, etc.NULL, etc.FAIL):
        assert x is not y
    with pytest.raises(etc.SentinelInitError):
        etc._SentinelType('y', -1)


def test_defined_sentinels():
    """Test the defined sentinel values."""
    cases = [
        (etc.PASS, 'PASS', True, True),
        (etc.NULL, 'NULL', None, False),
        (etc.FAIL, 'FAIL', False, False),
    ]
    for (this, name, value, truth) in cases:
        assert this is not value
        assert this == value
        assert bool(this) == truth
        assert str(this) == name
        x = this
        assert this is x
        assert this == x
        with pytest.raises(etc.SentinelValueError):
            etc.sentinel(name, this)


def test_isnull():
    """Test the function that excludes 0 from truthiness evaluation."""
    assert etc.isnull(None)
    assert etc.isnull([])
    assert etc.isnull(())
    assert etc.isnull(numpy.array([]))
    assert not etc.isnull(0)
    assert not etc.isnull(numpy.zeros((2, 2)))


def test_join():
    """Test the custom string-joining function."""
    assert etc.join(['a']) == 'a'
    assert etc.join(['a', 'b']) == 'a and b'
    assert etc.join(['a', 'b'], 'or') == 'a or b'
    assert etc.join(['a', 'b', 'c']) == 'a, b, and c'
    assert etc.join(['a', 'b', 'c'], 'or') == 'a, b, or c'
    assert etc.join(['a', 'b', 'c'], quoted=True) == "'a', 'b', and 'c'"


def test_allisinstance():
    """Test the custom instance-checking function."""
    assert etc.allisinstance(int, 1)
    assert etc.allisinstance(int, 1, 2)
    assert etc.allisinstance((int, numbers.Real), 1, 2)
    assert etc.allisinstance((int, float), 1, 2)
    assert not etc.allisinstance(int, 1, '1')
    with pytest.raises(TypeError):
        etc.allisinstance(int)


def test_widest():
    """Test the function that checks for the widest of two types."""
    class A0: ...
    class B0: ...
    class A1(A0): ...
    class B1(B0): ...
    class A2(A1): ...
    class X0(A1): ...
    assert etc.widest(A0(), A1()) == A1
    assert etc.widest(A0(), A2()) == A2
    assert etc.widest(X0(), A1()) == X0
    with pytest.raises(ValueError):
        assert etc.widest(X0(), A2())
    assert etc.widest(X0(), A2(), base=A1) == A1
    with pytest.raises(TypeError):
        assert etc.widest(A1(), B1(), base=A0)

