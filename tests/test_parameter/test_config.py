import typing

from eprempy.parameter._config import Defaults


def test_default_values(
    srcdir: str,
    default: typing.Dict[str, dict],
) -> None:
    """Compare the default value of each parameter to a reference value."""
    cfg = Defaults(srcdir=srcdir)
    for key, current in default.items():
        assert cfg[key] == current['defaultVal']


