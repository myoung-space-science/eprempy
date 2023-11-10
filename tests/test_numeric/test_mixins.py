import typing

import numpy
import pytest

from conftest import (
    Object,
    Functions,
)


def test_functions(
    object_factory: typing.Callable[..., Object],
    functions_factory: typing.Callable[..., Functions],
) -> None:
    """Test basic use of the `Functions` mixin class."""
    a = object_factory([4.0, 9.0], color='green')
    b = functions_factory([4.0, 9.0], color='green')
    with pytest.raises(TypeError):
        numpy.sqrt(a)
    with pytest.raises(TypeError):
        numpy.mean(a)
    x = numpy.sqrt(b)
    assert isinstance(x, type(b))
    assert numpy.array_equal(x.data, [2.0, 3.0])
    assert x.color == 'green'
    y = numpy.mean(b)
    assert isinstance(y, type(b))
    assert y.data == 6.5
    assert y.color == 'green'



