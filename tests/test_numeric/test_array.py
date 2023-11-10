import itertools

import numpy
import pytest

import support
from eprempy import numeric


def test_string_transpose(ndarrays: support.NDArrays):
    """Test the ability to transpose an array by dimensions."""
    ndarray = ndarrays.xyz
    dimensions = ['x', 'y', 'z']
    array = numeric.array(ndarray, dimensions=dimensions)
    assert array.transpose() is array
    for permutation in itertools.permutations(dimensions):
        axes = [dimensions.index(d) for d in permutation]
        expected = ndarray.transpose(axes)
        byname = array.transpose(permutation)
        byaxis = array.transpose(axes)
        for x in (byname, byaxis):
            assert isinstance(x, numeric.Array)
            assert x.dimensions == permutation
            assert numpy.array_equal(x, expected)
    with pytest.raises(ValueError):
        array.transpose('x', 'w', 'y', 'z')
    with pytest.raises(ValueError):
        array.transpose('x', 'z')


