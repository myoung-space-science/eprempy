"""
EPREM observer interfaces.
"""

# XXX: This structure comes from an earlier version of this package that did not
# have separate __init__.py and eprem.py modules. It may be one level of
# abstraction too many.
from .observer import (
    Stream,
    Point,
    stream_factory as stream,
    point_factory as point,
)


__all__ = [
    "Stream",
    "Point",
    "stream",
    "point",
]

