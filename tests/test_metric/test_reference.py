import pytest

from eprempy import metric


@pytest.fixture
def definitions():
    """The reference mapping of defined unit conversions."""
    return metric._reference._CONVERSIONS


def test_defined_conversions(definitions: dict):
    """Test the collection of defined conversions."""
    assert len(metric.CONVERSIONS) == 2 * len(definitions)
    for (u0, u1), wt in definitions.items():
        assert (u0, u1) in metric.CONVERSIONS
        assert metric.CONVERSIONS.get_weight(u0, u1) == wt
        assert metric.CONVERSIONS.get_weight(u1, u0) == 1 / wt


