import os
import pathlib
import shutil
import typing

from . import etc


PathLike = typing.Union[str, os.PathLike]


class PathTypeError(Exception):
    """The path is the wrong type."""


class PathOperationError(Exception):
    """This operation is not allowed on the given path(s)."""


def normalize(p: PathLike):
    """Expand and resolve the given path."""
    return pathlib.Path(p).expanduser().resolve()


def localize(p: PathLike, normalized: bool=False):
    """Convert `p` to local path.
    
    This function simply ensures that the return value is an instance of
    ``pathlib.Path`` without parents. It may be useful for ensuring that future
    operations don't write to an arbitrary location on disk.

    Parameters
    ----------
    p : path-like
        A representation of the path to convert.

    normalized : bool, default=False
        If true, expand `~` and fully resolve `p` before extracting its final
        component. By default, this function will create an intermediate path
        from `p` as-is.
    """
    path = normalize(p) if normalized else pathlib.Path(p)
    return pathlib.Path(path.name)


def locate(
    name: str,
    path: pathlib.Path,
    environment: typing.Dict[str, str]
) -> pathlib.Path:
    """Compute an appropriate path to the named element.

    Notes
    -----
    * Intended for use by `~Project`.
    * This function will attempt to create a full path (resolving links as
      necessary) based on `environment` or from `path / name`. If neither exist,
      it will return `name` as-is, thereby allowing calling code to default to
      the searching the system path.
    """
    location = environment.get(name) or path / name
    it = normalize(os.path.realpath(location))
    return it if it.exists() else pathlib.Path(shutil.which(name))


class PathSet(etc.InstanceSet):
    """A metaclass for sets of path-based objects.

    Using this class as the metaclass for a class that manages path-based
    objects (e.g., datasets) will ensure that only one instance of the object
    exists. This may be useful when multiple other objects need to access an
    instance of the class given a common path.

    See https://refactoring.guru/design-patterns/singleton/python/example
    """

    _instances = {}

    def _generate_key(self, *args, **kwargs):
        path = kwargs.get('path')
        if path is None and len(args) >= 1:
            path = args[0]
        if isinstance(path, (str, pathlib.Path)):
            return path
        return super()._generate_key(*args, **kwargs)


class NonExistentPathError(Exception):

    def __init__(self, path: str=None):
        self._path = path

    @property
    def path(self) -> str:
        if self._path is None:
            self._path = "The requested path"
        return self._path

    def __str__(self):
        return f"{self.path} does not exist."


def fullpath(path: PathLike, strict: bool=False):
    """Expand and resolve `path`.

    Parameters
    ----------
    path : string or `os.PathLike`
        The target path.
    strict : bool, default=False
        If true and the computed path does not exist, raise an exception.
        Otherwise, this function will return the new path.

    Returns
    -------
    `pathlib.Path`

    Raises
    ------
    `~NonExistentPathError`: See `strict` keyword.
    """
    new = pathlib.Path(path).expanduser().resolve()
    if strict and not new.exists():
        raise NonExistentPathError(path)
    return new


Parsable = typing.TypeVar('Parsable')
Parsable = typing.Dict[str, typing.Any]


class TextFile:
    """A representation of a text file with pattern-based search."""

    def __init__(self, path: PathLike) -> None:
        """
        Parameters
        ----------
        path : string or `pathlib.Path`
            The path to the target text file. May be relative and contain
            wildcards.
        """
        self._path = path
        self._lines = None

    @property
    def lines(self):
        """The lines of text in this file."""
        if self._lines is None:
            with self.path.open('r') as fp:
                self._lines = fp.readlines()
        return self._lines

    @property
    def path(self):
        """The fully resolved path."""
        return fullpath(self._path)

    KT = typing.TypeVar('KT', bound=typing.Hashable)

    VT = typing.TypeVar('VT')

    Matched = typing.TypeVar('Matched')

    Parsed = typing.TypeVar('Parsed', bound=tuple)

    Parsed = typing.Tuple[KT, VT]

    def extract(
        self,
        match: typing.Callable[[str], Matched],
        parse: typing.Callable[[Matched], Parsed],
    ) -> typing.Dict[KT, VT]:
        """Search each line and parse those that meet given criteria.
        
        Parameters
        ----------
        match : callable
            A callable object that takes a string and returns matches to a
            pattern.
        parse : callable
            A callable object that takes the output of `match`, and returns a
            tuple containing a valid mapping key and corresponding value. It may
            assume that the input is not empty.

        Returns
        -------
        dict
            A dictionary constructed from the tuples output by `parse`.
        """
        matches = [match(line) for line in self.lines]
        parsed = [parse(match) for match in matches if match]
        return dict(parsed)

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return str(self.path)

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        return str(self.path)


def file_lines(file: PathLike) -> int:
    """Count the number of lines in a file."""
    with pathlib.Path(file).open('r') as fp:
        nlines = len(fp.readlines())
    return nlines


def strip_inline_comments(string: str, comments: typing.Iterable[str]) -> str:
    """Remove inline comments from a string."""
    for c in comments:
        parts = string.split(c)
        string = parts[0]
    return string.strip()


def search(file: PathLike, *paths: PathLike) -> pathlib.Path:
    """Search `paths` for `file`.
    
    Parameters
    ----------
    file : path-like
        The file to locate

    paths : path-like
        Zero or more paths to search, in the order given. Each member must be an
        object that can represent a path on the current file system. If missing,
        this function will search the current working directory.

    Returns
    -------
    `pathlib.Path` or `None`
        The full path to the file, if found.
    """
    for p in list(paths) + [pathlib.Path.cwd()]:
        path = fullpath(p, strict=True)
        if path.is_dir():
            test = path / str(file)
            if test.exists():
                return test


def find_file_by_template(
    templates: typing.List[typing.Callable],
    name: str,
    directory: PathLike=pathlib.Path.cwd(),
) -> pathlib.Path:
    """Find a valid path that conforms to a given template."""
    d = fullpath(directory, strict=True)
    for template in templates:
        test = d / str(template(name))
        if test.exists():
            return test


