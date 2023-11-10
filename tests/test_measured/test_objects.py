"""
General tests for all measured objects.
"""

from eprempy import measured


def test_unitless_default():
    """The default unit of a measured object should be '1'."""
    objects = (
        measured.value(1.5),
        measured.sequence([1.5]),
    )
    for this in objects:
        assert this.unit == '1'
        assert this.isunitless


def test_unit_conversion():
    """Test the default unit-conversion logic on a measured object."""
    cases = (
        measured.value(1.5, 'm'),
        measured.sequence([1.5], 'm'),
    )
    for x in cases:
        for arg in ('cm', 'cgs'):
            y = x.withunit(arg)
            assert y is not x
            assert x.unit == 'm'
            assert x.data == 1.5
            assert y.unit == 'cm'
            assert y.data == 150.0
    nuc = measured.value(1.0, 'nuc')
    assert nuc.withunit('mks').unit == 'kg'
    assert nuc.withunit('cgs').unit == 'g'


