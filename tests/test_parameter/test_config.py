import typing

from eprempy import parameter
from eprempy import paths


def test_default_values(
    srcdir: str,
    default: typing.Dict[str, dict],
) -> None:
    """Compare the default value of each parameter to a reference value."""
    cfg = parameter.defaults(srcdir=srcdir)
    assert isinstance(cfg, parameter.Defaults)
    for key, current in default.items():
        assert cfg[key] == current['defaultVal']


def test_configfile() -> None:
    """Parse a sample configuration file."""
    path = paths.fullpath(__file__).parent / 'sample.cfg'
    cfg = parameter.configfile(path)
    assert isinstance(cfg, parameter.ConfigFile)
    assert cfg['a'] == "1"
    assert cfg['b'] == "2"
    assert cfg['c'] == "3"
    assert cfg['name'] == "'value'"
    assert cfg['this'] == "'that'"

