"""
Tools and scripts for analyzing EPREM simulation runs.
"""

# read version from installed package
from importlib.metadata import version
__version__ = version("eprempy")

from .physical import Array
from .observable import Quantity as Observable


__all__ = [
    "Array",
    "Observable",
]

