import typing

import pytest

from conftest import Object
from eprempy import numeric


def test_spawn(object_factory: typing.Callable[..., Object]):
    """"""
    @Object.register.factory
    def factory(*args, **kwargs):
        return object_factory(*args, **kwargs)
    value = 1.5
    color = 'red'
    a = factory(value, color=color)
    b = Object.spawn(value, color=color)
    c = a.spawn(value, color=color)
    assert a == b
    assert a == c
    with pytest.raises(NotImplementedError):
        numeric.Object.spawn(value)
    with pytest.raises(NotImplementedError):
        numeric.Object(value).spawn(value)


