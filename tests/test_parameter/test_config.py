import typing

from eprempy.parameter._config import Defaults


def test_default_values(
    srcdir: str,
    reference: typing.Dict[str, dict],
) -> None:
    """Compare the default value of each parameter to a reference value."""
    cfg = Defaults(srcdir=srcdir)
    for key, current in reference.items():
        assert cfg[key] == current['default']


