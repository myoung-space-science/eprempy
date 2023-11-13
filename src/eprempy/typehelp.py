"""
Additional support for type annotations.

This module provides a single interface to extended type annotations. For
example, suppose `BestType` is available in the `typing` module starting with
Python version 3.X, and is available in the `typing_extensions` module for
earlier versions. This module will check the version of the active Python
interpreter and will import from either `typing` or `typing_extensions` as
appropriate, so that other modules may simply access `typehelp.BestType`.
"""

import sys

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


__all__ = [
    "Self",
]

