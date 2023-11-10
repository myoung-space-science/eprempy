import pathlib

import pytest

from eprempy import paths

# TODO: Generalize test paths beyond *nix systems.


def test_fullpath():
    """Test the object that represents a fully-qualified path."""
    test = {
        '~/Downloads': True,
        '/does/not/exist': False,
    }
    for this, existent in test.items():
        path = paths.fullpath(this)
        assert path == pathlib.Path(this).expanduser().resolve()
        assert path.exists() == existent
        if not existent:
            with pytest.raises(paths.NonExistentPathError):
                paths.fullpath(this, strict=True)


def test_search():
    """Test the function that searches for a file."""
    p = pathlib.Path('~/Downloads/test-file.txt').expanduser().resolve()
    name = p.name
    assert paths.search(name) is None
    assert paths.search(name, '~/Downloads') is None
    p.touch()
    assert paths.search(name) is None
    assert paths.search(name, '~/Downloads') == p
    p.unlink()

