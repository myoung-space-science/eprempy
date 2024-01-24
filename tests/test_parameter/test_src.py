import pytest

from eprempy import paths
from eprempy.parameter import default
from eprempy.parameter._src import (
    BaseTypesH,
    ConfigurationC,
)


def test_basetypes_h(srcdir: str):
    """Regression test for values defined in src/baseTypes.h."""
    for path in (srcdir, None):
        b = BaseTypesH(path)
        if path is not None:
            assert b.origin.parent == paths.fullpath(path, strict=True)
        for key, this in default.BASETYPES_H.items():
            assert b[key] == pytest.approx(this['value'])


def test_configuration_c(srcdir: str):
    """Make sure the object contains everything in src/configuration.c."""
    testkeys = {'type', 'defaultVal', 'minVal', 'maxVal'}
    for path in (srcdir, None):
        c = ConfigurationC(path)
        if path is not None:
            assert c.origin.parent == paths.fullpath(path, strict=True)
        for key, this in default.CONFIGURATION_C.items():
            expected = {k: v for k, v in this.items() if k in testkeys}
            assert c[key] == expected


