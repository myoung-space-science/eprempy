"""
This module exists to make sure each `__all__` is up to date.
"""

from eprempy.base import *
from eprempy.datafile import *
from eprempy.measurable import *
from eprempy.measured import *
from eprempy.metric import *
from eprempy.numeric import *
from eprempy.observable import *
from eprempy.parameter import *
from eprempy.physical import *
from eprempy.quantity import *
from eprempy.real import *
from eprempy.symbolic import *


def test_true():
    """Unconditionally succeed.

    This "test" is a placeholder. If any of the attempts to `import *` fail,
    this test will never run. If they all succeed, this test will cause the test
    runner to indicate that the entire module succeeded.
    """
    assert True


