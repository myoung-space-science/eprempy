import pytest

from eprempy import exceptions


class InversionError(Exception):
    """Custom error type for exception tests."""


def invert(v):
    """Example function for tests."""
    if v == -1:
        raise InversionError
    return 1 / v


def test_wrapper_basic():
    """Test the class that converts exceptions into values."""
    wrapper = exceptions.Wrapper(invert)
    wrapper.catch(TypeError)
    wrapper.catch(ZeroDivisionError, 'Bad!')
    # valid call
    assert wrapper.compute(2) == 0.5
    # catch TypeError
    assert wrapper.compute('2') is None
    # catch ZeroDivisionError
    assert wrapper.compute(0) == 'Bad!'
    with pytest.raises(InversionError):
        wrapper.compute(-1)


def test_wrapper_ellipsis():
    """Test the special case of `...` as default value for Wrapper."""
    def check(*args, **kwargs):
        if (args and args[0] < 0) or len(kwargs) > 2:
            raise ValueError
        return True
    wrapper = exceptions.Wrapper(check)
    wrapper.catch(ValueError, ...)
    # valid call
    assert wrapper.compute(4, 5)
    # valid call
    assert wrapper.compute(a=5, b=5)
    # catch ValueError due to illegal value; return single positional argument
    assert wrapper.compute(-1) == -1
    # catch ValueError due to illegal value; return a tuple containing all
    # positional arguments
    assert wrapper.compute(-1, 5, 6) == (-1, 5, 6)
    # catch ValueError due to the presence of extra keyword arguments; return a
    # dict containing all keyword arguments
    assert wrapper.compute(a=4, b=5, c=6) == {'a': 4, 'b':5, 'c': 6}
    # catch ValueError due to illegal value; return a tuple containing a tuple
    # of positional arguments and a dict of keyword arguments.
    assert wrapper.compute(-1, 5, 6, this=7) == ((-1, 5, 6), {'this': 7})


def test_convert():
    """Test the decorator function that converts exceptions."""
    # Replace an expected exception with a value.
    @exceptions.convert(InversionError, None)
    def f(x):
        return invert(x)
    # Replace an expected exception with a different exception.
    @exceptions.convert(InversionError, ValueError)
    def g(x):
        return invert(x)
    # Make sure we didn't mangle the original function.
    with pytest.raises(InversionError):
        invert(-1)
    # Make sure the decorated functions behave as expected.
    assert f(2) == 0.5
    assert g(2) == 0.5
    # Test the `return` form of the decorator.
    assert f(-1) is None
    # Test the `raise` form of the decorator.
    with pytest.raises(ValueError):
        g(-1)


def test_isexception():
    """Test the function that checks for a subtype of `Exception`."""
    true = (
        Exception,
        TypeError,
        ValueError,
        AssertionError,
    )
    for this in true:
        assert exceptions.isexception(this)
    false = (
        None,
        0,
        1,
        'string',
        int,
    )
    for this in false:
        assert not exceptions.isexception(this)


