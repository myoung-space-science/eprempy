import pytest

from eprempy import base


class Empty:
    __eq__ = None
    __ne__ = None
    __lt__ = None
    __le__ = None
    __gt__ = None
    __ge__ = None


@pytest.fixture
def empty():
    """Create an empty test quantity."""
    return Empty()


def trivial(*args, **kwargs):
    return NotImplemented


class Ordered:
    __lt__ = trivial
    __le__ = trivial
    __gt__ = trivial
    __ge__ = trivial


@pytest.fixture
def ordered():
    """Create an ordered test quantity."""
    return Ordered()


class Comparable(Ordered):
    __eq__ = trivial
    __ne__ = trivial


@pytest.fixture
def comparable():
    """Create an comparable test quantity."""
    return Comparable()


class Additive:
    __add__ = trivial
    __radd__ = trivial
    __sub__ = trivial
    __rsub__ = trivial


@pytest.fixture
def additive():
    """Create an additive test quantity."""
    return Additive()


class Multiplicative:
    __mul__ = trivial
    __rmul__ = trivial
    __truediv__ = trivial
    __rtruediv__ = trivial


@pytest.fixture
def multiplicative():
    """Create a multiplicative test quantity."""
    return Multiplicative()


class Algebraic(Additive, Multiplicative):
    __pow__ = trivial


@pytest.fixture
def algebraic():
    """Create an algebraic test quantity."""
    return Algebraic()


class Complex(Algebraic):
    __abs__ = trivial
    __pos__ = trivial
    __neg__ = trivial


@pytest.fixture
def complex():
    """Create a complex-valued test quantity."""
    return Complex()


class Real(Comparable, Complex):
    __floordiv__ = trivial
    __rfloordiv__ = trivial
    __mod__ = trivial
    __rmod__ = trivial


@pytest.fixture
def real():
    """Create a real-valued test quantity."""
    return Real()


class Sequence:
    __contains__ = trivial
    __len__ = trivial
    __iter__ = trivial
    __getitem__ = trivial
    __array__ = trivial


@pytest.fixture
def sequence():
    """Create a sequence-like test quantity."""
    return Sequence()


class Array(Sequence):
    @property
    def size(self):
        pass
    @property
    def ndim(self):
        pass
    @property
    def shape(self):
        pass


@pytest.fixture
def array():
    """Create an array-like test quantity."""
    return Array()


class Scalar(Real):
    __int__ = trivial
    __float__ = trivial
    __round__ = trivial


@pytest.fixture
def scalar():
    """Create a scalar test quantity."""
    return Scalar()


class Variable(Sequence):
    __int__ = trivial
    __float__ = trivial
    __complex__ = trivial
    @property
    def size(self):
        pass


@pytest.fixture
def variable():
    """Create a variable test quantity."""
    return Variable()


class Measured:
    @property
    def data(self):
        pass
    @property
    def unit(self):
        pass


@pytest.fixture
def measured():
    """Create a measured test quantity."""
    return Measured()


class Measurable:
    def __measure__(self):
        return Measured()


@pytest.fixture
def measurable():
    """Create a measurable test quantity."""
    return Measurable()


class Measurement(Measured, Variable): ...


@pytest.fixture
def measurement():
    """Create a measurement-like test quantity."""
    return Measurement()


def test_isordered(ordered, empty):
    """Test the check for ordered quantities."""
    assert base.isordered(ordered)
    assert not base.isordered(empty)


def test_iscomparable(comparable, empty):
    """Test the check for comparable quantities."""
    assert base.iscomparable(comparable)
    assert not base.iscomparable(empty)


def test_isadditive(additive, empty):
    """Test the check for additive quantities."""
    assert base.isadditive(additive)
    assert not base.isadditive(empty)


def test_ismultiplicative(multiplicative, empty):
    """Test the check for multiplicative quantities."""
    assert base.ismultiplicative(multiplicative)
    assert not base.ismultiplicative(empty)


def test_isalgebraic(algebraic, comparable, additive, multiplicative, empty):
    """Test the check for algebraic quantities."""
    assert base.isalgebraic(algebraic)
    for this in (empty, comparable, additive, multiplicative):
        assert not base.isalgebraic(this)


def test_iscomplex(complex, algebraic, empty):
    assert base.iscomplex(complex)
    for this in (empty, algebraic):
        assert not base.iscomplex(this)


@pytest.mark.xfail
def test_isreal(real, empty):
    """Test the check for real quantities."""
    assert isreal(real)
    assert not base.isreal(empty)


def test_issequence(sequence, scalar, empty):
    """Test the check for sequence-like quantities."""
    assert not isreal(sequence)
    assert base.issequence(sequence)
    for this in (empty, scalar):
        assert not base.issequence(this)


def test_isarray(array, sequence, scalar, empty):
    """Test the check for array-like quantities."""
    assert not isreal(array)
    assert base.isarray(array)
    for this in (empty, scalar, sequence):
        assert not base.isarray(this)


@pytest.mark.xfail
def test_isscalar(array, scalar, empty):
    """Test the check for scalar quantities."""
    assert isreal(scalar)
    assert base.isscalar(scalar)
    for this in (empty, array):
        assert not base.isscalar(this)


def test_isvariable(variable, array, scalar, empty):
    """Test the check for variable quantities."""
    assert not isreal(variable)
    assert base.isvariable(variable)
    for this in (array, scalar, empty):
        assert not base.isvariable(this)


def test_ismeasured(measured, real, empty):
    """Test the check for measured quantities."""
    assert base.hasdata(measured)
    assert base.hasunit(measured)
    assert base.ismeasured(measured)
    for this in (empty, real):
        assert not base.ismeasured(this)


def test_ismeasurement(measurement, measured, variable, real, empty):
    """Test the check for measurement-like quantities."""
    assert base.hasdata(measurement)
    assert base.hasunit(measurement)
    assert base.ismeasured(measurement)
    assert base.isvariable(measurement)
    assert base.ismeasurement(measurement)
    for this in (empty, real, measured, variable):
        assert not base.ismeasurement(this)


def isreal(this):
    """Helper function for tests of real-valued quantities."""
    return (
        base.isordered(this) and
        base.isadditive(this) and
        base.ismultiplicative(this) and
        base.isreal(this)
    )


def test_ismeasurable(measurable, array, scalar, empty):
    """Test the check for measurable quantities."""
    assert base.ismeasurable(measurable)
    for this in (empty, scalar, array):
        assert not base.ismeasurable(this)


