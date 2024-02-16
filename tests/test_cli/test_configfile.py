import filecmp
import pathlib
import subprocess
import typing

import pytest

from eprempy import cli


@pytest.fixture
def argsdict():
    return {
            '0': {},
            '1': {
                'useDegrees': 0,
                'idealShockWidth': 0.7853981634,
            },
            '2': {
                'useDegrees': 1,
                'idealShockWidth': 45.0,
            },
            '3': {
                'idealShockWidth': 0.7853981634,
            },
    }


def write_files(
    argsdict: typing.Dict[str, dict],
) -> typing.Tuple[pathlib.Path]:
    """Create temporary config files for testing."""
    written = []
    for key, args in argsdict.items():
        path = tmpfile(key)
        with path.open('w') as fp:
            fp.writelines([f"{k}={v}\n" for k, v in args.items()])
        written.append(path)
    return tuple(written)


def remove_files(filepaths: typing.Iterable[pathlib.Path]):
    """Remove temporary config files."""
    for key in filepaths:
        tmpfile(key).unlink()


def tmpfile(key: str):
    """Define a temporary file path based on `key`."""
    return pathlib.Path(f"config-{key}.cfg")


def test_diff(argsdict):
    """"""
    filepaths = write_files(argsdict)
    pathstr = ' '.join(str(filepath) for filepath in filepaths)
    command = f"python -m eprempy configfile -c {pathstr} --diff"
    with pathlib.Path('result-diff.txt').open('w') as fp:
        subprocess.run(
            command,
            stdout=fp,
            stderr=subprocess.STDOUT,
            shell=True,
        )
    assert filecmp.cmp('expected-diff.txt', 'result-diff.txt')
    for filepath in filepaths:
        filepath.unlink()
