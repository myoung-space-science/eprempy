import typing

from eprempy import dataset
from eprempy import reference


def test_arrays():
    """Test metadata for arrays."""
    check(reference.ARRAYS, dataset.ARRAYS)


def test_scalars():
    """Test metadata for scalars."""
    check(reference.SCALARS, dataset.SCALARS)


def test_axes():
    """Test metadata for axes."""
    check(reference.AXES, dataset.AXES)


def test_observables():
    """Test metadata for observables."""
    check(reference.OBSERVABLES, reference._metadata.keys())


def check(subset: reference.Subset, names: typing.Iterable[str]):
    """Run common tests on the given subset."""
    for name in names:
        aliases = reference.ALIASES.get(name, [name])
        assert name in aliases
        for alias in aliases:
            assert alias in subset.aliases
            assert subset.names[alias] == name


