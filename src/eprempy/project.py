"""
The interactive EPREM runtime interface.
"""

import argparse
import collections.abc
import contextlib
import datetime
import json
import os
import pathlib
import shutil
import subprocess
import sys
import typing

try:
    import isort
    _HAVE_ISORT = True
except ModuleNotFoundError:
    _HAVE_ISORT = False
try:
    import yaml
    _HAVE_YAML = True
except ModuleNotFoundError:
    _HAVE_YAML = False

FILEPATH = pathlib.Path(__file__)
DIRECTORY = FILEPATH.parent
sys.path.append(str(DIRECTORY))

from . import interfaces
from . import etc
from . import paths


class LogKeyError(KeyError):
    """The log has no entry for a given key."""


class ReadTypeError(Exception):
    """There is no support for reading a given file type."""


RunLogType = typing.TypeVar('RunLogType', bound='RunLog')


class RunLog(collections.abc.Mapping):
    """Mapping-based interface to an EPREM project log."""

    def __init__(self, path: paths.PathLike, **common) -> None:
        """Create a new project log.
        
        Parameters
        ----------
        path : path-like
            The path to the log file, including the file name. If the file does
            not exist, this class will create a new one; otherwise, this class
            will use the existing file. The path may be relative to the current
            directory.

        common
            Key-value pairs of attributes that are common to all runs. Not
            allowed when retrieving an existing file.

        Raises
        ------
        TypeError
            Caller attempted to set common attributes on an existing log.
        """
        full = paths.normalize(path)
        if full.exists():
            self._path = full
            if common:
                raise TypeError(
                    "Cannot change common attributes "
                    "of an existing log"
                ) from None
        else:
            self._path = full
            self.dump(common)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self._asdict)

    def __iter__(self) -> typing.Iterator[str]:
        """Called for iter(self)."""
        return iter(self._asdict)

    def __getitem__(self, __k: str):
        """Get metadata for a run."""
        if __k in self._asdict:
            return self._asdict[__k]
        raise LogKeyError(f"Unknown run {__k!r}")

    def update_directory(self, target: paths.PathLike):
        """Update the directory path to this file.

        Parameters
        ----------
        target : path-like
            The directory to which to move this file. May be relative.

        Raises
        ------
        PathTypeError
            The target path does not exist or is not a directory.

        Notes
        -----
        * This method assumes that the target path exists.
        * This method does not allow changes to the file name.
        """
        new = paths.normalize(target)
        if not new.exists():
            raise paths.PathTypeError("The new path must exist") from None
        if not new.is_dir():
            raise paths.PathTypeError("Cannot rename log file") from None
        self._path = new / self.name
        source = str(self.path.parent)
        for key in self:
            self.mv(key, key.replace(source, str(new)))
        return self

    @typing.overload
    def create(
        self: RunLogType,
        key: str,
        mapping: typing.Mapping
    ) -> RunLogType:
        """Create a new entry from a mapping."""

    @typing.overload
    def create(
        self: RunLogType,
        key: str,
        **items
    ) -> RunLogType:
        """Create a new entry from key-value pairs."""

    def create(
        self: RunLogType,
        key: paths.PathLike,
        *mapping: typing.Mapping,
        **items
    ) -> RunLogType:
        contents = self._asdict.copy()
        if mapping and items:
            raise TypeError(
                f"{self.__class__.__qualname__}.create accepts"
                " a single mapping or multiple key-value pairs"
                ", but not both"
            ) from None
        new = dict(*mapping) or items
        contents[str(key)] = new
        self.dump(contents)
        return self

    def load(
        self: RunLogType,
        key: paths.PathLike,
        source: paths.PathLike,
        filetype: str=None
    ) -> RunLogType:
        """Create a new entry in this log file from a file."""
        contents = self._asdict.copy()
        contents[str(key)] = self._read_from_file(source, filetype)
        self.dump(contents)
        return self

    def _read_from_file(self, source, filetype):
        """Update the current contents from the `source` file."""
        contents = self._asdict.copy()
        loader = self._source_loader(filetype or pathlib.Path(source).suffix)
        with pathlib.Path(source).open('r') as fp:
            if loaded := loader(fp):
                contents.update(loaded)
        return contents

    def _source_loader(self, filetype: str):
        """Get a format-specific file-reader."""
        if filetype.lower().lstrip('.') == 'yaml':
            if _HAVE_YAML:
                return yaml.safe_load
            raise ReadTypeError("No support for reading YAML") from None
        if filetype.lower().lstrip('.') == 'json':
            return json.load
        raise ValueError(
            f"Unknown file type: {filetype!r}"
        ) from None

    def append(self, target: paths.PathLike, key: str, value):
        """Append metadata to `target`."""
        contents = self._asdict.copy()
        run = str(target)
        try:
            record = contents[run]
        except KeyError as err:
            raise LogKeyError(
                f"Cannot append to unknown run {run!r}"
            ) from err
        record[key] = value
        self.dump(contents)
        return self

    def mv(self, source: paths.PathLike, target: paths.PathLike):
        """Rename `source` to `target` in this log file."""
        old = str(source)
        new = str(target)
        if old not in self:
            raise LogKeyError(
                f"Cannot rename unknown run {old!r}"
            ) from None
        updated = {k: v for k, v in self._asdict.items() if k != old}
        updated[new] = self._asdict[old]
        self.dump(updated)
        return self

    def rm(self, target: paths.PathLike):
        """Remove the target run from this log file."""
        updated = {k: v for k, v in self._asdict.items() if k != str(target)}
        self.dump(updated)
        return self

    @property
    def _asdict(self) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        """Internal dictionary representing the current contents."""
        with self.path.open('r') as fp:
            return dict(json.load(fp))

    def dump(self, contents: typing.Mapping):
        """Write `contents` to this log file."""
        payload = {
            k: str(v) if isinstance(v, pathlib.Path) else v
            for k, v in contents.items()
        }
        with self.path.open('w') as fp:
            json.dump(payload, fp, indent=4, sort_keys=True)

    @property
    def name(self):
        """The name of this log file.
        
        Same as `RunLog.path.name`.
        """
        return self.path.name

    @property
    def path(self):
        """The path to this log file."""
        return self._path

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return str(self._asdict)

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        return f"{self.__class__.__qualname__}({self.path})"


class ProjectExistsError(Exception):
    """A project with this name already exists."""


_Paths = typing.TypeVar('_Paths')
_Paths = typing.Union[pathlib.Path, typing.Tuple[pathlib.Path, pathlib.Path]]


class _PathOperation(collections.abc.Iterable):
    """Helper for path-based operations."""

    @typing.overload
    def __init__(
        self,
        operator: typing.Callable[
            [pathlib.Path],
            typing.Union[pathlib.Path, paths.PathOperationError]
        ],
        paths: typing.Iterable[pathlib.Path]=None,
    ) -> None: ...

    @typing.overload
    def __init__(
        self,
        operator: typing.Callable[
            [pathlib.Path, pathlib.Path],
            typing.Union[pathlib.Path, paths.PathOperationError]
        ],
        paths: typing.Iterable[typing.Tuple[pathlib.Path, pathlib.Path]]=None,
    ) -> None: ...

    def __init__(self, operator, paths=None) -> None:
        """Create a new instance."""
        self.operator = operator
        self._paths = paths
        self._force = None
        self._silent = None

    def __bool__(self) -> bool:
        """Called for bool(self)."""
        return bool(self._paths)

    def __iter__(self):
        """Iteratively apply the operation, if possible."""
        error = None
        for path in self._paths:
            result = self.apply(path)
            if not isinstance(result, paths.PathOperationError):
                yield result
                error = False
            else:
                error = True
            if error:
                if not self._force:
                    raise result
                if not self._silent:
                    print(result)

    def errors(self, force: bool=False, silent: bool=False):
        """Update how this instance handles errors and warnings."""
        self._force = force
        self._silent = silent
        return self

    def apply(
        self,
        this
    ) -> typing.Union[pathlib.Path, typing.Tuple[pathlib.Path]]:
        """Apply the operator to `this`, if possible."""
        if isinstance(this, pathlib.Path):
            return self.operator(this)
        try:
            allpaths = all(isinstance(i, pathlib.Path) for i in this)
        except TypeError:
            allpaths = False
        if allpaths:
            return self.operator(*this)


# TODO: Python >= 3.9
# - list[typing.Union[pathlib.Path, tuple[pathlib.Path, ...]]]

# TODO: Python >= 3.10
# - list[pathlib.Path | tuple[pathlib.Path, ...]]

ListOfPathsOrPathTuples = typing.TypeVar('ListOfPathsOrPathTuples')
ListOfPathsOrPathTuples = typing.List[
    typing.Union[pathlib.Path, typing.Tuple[pathlib.Path, ...]]
]

RunPathsType = typing.TypeVar('RunPathsType', bound='RunPaths')


class RunPaths(collections.abc.Collection):
    """Manager for path operations on runtime directories."""

    def __init__(
        self,
        root: paths.PathLike,
        branches: typing.Iterable[str]=None,
        base: str=None,
    ) -> None:
        self._root = paths.normalize(root)
        self._base = base or 'runs'
        self._branches = branches
        self._listing = None
        for directory in self.listing:
            directory.mkdir(parents=True, exist_ok=True)

    def update(
        self: RunPathsType,
        root: paths.PathLike=None,
        branches: typing.Iterable[str]=None,
        base: str=None,
    ) -> RunPathsType:
        """Update path components."""
        self._listing = None
        if root:
            path = paths.normalize(root)
            if path.exists():
                raise paths.PathTypeError(
                    f"Renaming {self.root.name!r} to {path.name!r} would "
                    f"overwrite {path}."
                )
            self.root.rename(path)
            self._root = path
        if branches:
            self._branches = branches
        if base:
            self._base = base
        return self

    def __contains__(self, __x: paths.PathLike) -> bool:
        """Called for __x in self."""
        return __x in self.listing

    def __iter__(self) -> typing.Iterator[pathlib.Path]:
        """Called for iter(self)."""
        return iter(self.listing)

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.listing)

    def mkdir(
        self,
        target: paths.PathLike,
        branches: typing.Union[str, typing.Iterable[str]]=None,
    ) -> _PathOperation:
        """Create target run(s) if possible."""
        return _PathOperation(
            self._mkdir,
            paths=self.define(target, branches=branches),
        )

    def _mkdir(self, target: paths.PathLike):
        """Create the target run if safe to do so."""
        this = paths.normalize(target)
        if this.exists():
            return paths.PathOperationError(
                f"Cannot create {str(this)!r}: already exists"
            )
        this.mkdir(parents=True)
        return this

    def mv(
        self,
        source: paths.PathLike,
        target: paths.PathLike,
        branches: typing.Union[str, typing.Iterable[str]]=None,
    ) -> _PathOperation:
        """Rename `source` to `target` where possible."""
        pairs = self.define(source, target, branches=branches)
        return _PathOperation(self._mv, paths=pairs)

    def _mv(self, source: paths.PathLike, target: paths.PathLike):
        """Rename `source` to `target` only if safe to do so."""
        this = paths.normalize(source)
        that = paths.normalize(target)
        if not this.exists():
            return paths.PathOperationError(
                f"Cannot rename {this}: does not exist"
            )
        if not this.is_dir():
            return paths.PathOperationError(
                f"Cannot rename {this}: not a directory"
            )
        if that.exists():
            return paths.PathOperationError(
                f"Renaming {this.name!r} to {that.name!r} would "
                f"overwrite {that}."
            )
        this.rename(that)
        return (this, that)

    def rm(
        self,
        target: paths.PathLike,
        branches: typing.Union[str, typing.Iterable[str]]=None,
    ) -> _PathOperation:
        """Remove target run(s), if possible."""
        return _PathOperation(
            self._rm,
            paths=self.define(pattern=target, branches=branches),
        )

    def _rm(self, target: paths.PathLike):
        """Remove the target path only if safe to do so."""
        this = paths.normalize(target)
        if not this.exists():
            return paths.PathOperationError(
                f"Cannot remove {this}: does not exist"
            )
        if not this.is_dir():
            return paths.PathOperationError(
                f"Cannot remove {this}: not a directory"
            )
        shutil.rmtree(this)
        return this

    def define(
        self,
        *names: str,
        pattern: str=None,
        branches: typing.Union[str, typing.Iterable[str]]=None,
    ) -> ListOfPathsOrPathTuples:
        """Build a list of paths or tuples of paths.
        
        Parameters
        ----------
        *names : string
            Zero or more names of runtime directories to create.
        """
        rundirs = self._get_rundirs(branches)
        if pattern:
            return [
                path for rundir in rundirs
                for path in rundir.glob(pattern)
            ]
        if len(names) == 1:
            name = names[0]
            return [rundir / name for rundir in rundirs]
        if not names:
            return self.define(pattern='*', branches=branches)
        return [tuple(rundir / name for name in names) for rundir in rundirs]

    def resolve(self, target: str, branches: typing.Iterable[str]=None):
        """Compute the full path(s) to the target run."""
        if not branches:
            return [self.root / self.base / target]
        return [
            self.root / branch / self.base / target
            for branch in branches
        ]

    @property
    def runs(self) -> typing.Dict[str, typing.Set[str]]:
        """The available runs, and owning branches, if any."""
        if not self._branches:
            return {
                run.name: set()
                for run in (self.root / self.base).glob('*')
            }
        base = {
            run.name: set()
            for branch in self._branches
            for run in (self.root / branch / self.base).glob('*')
        }
        for run, branches in base.items():
            branches.update(
                branch for branch in self._branches
                if (self.root / branch / self.base / run).is_dir()
            )
        return base

    @property
    def branches(self):
        """The project branches, if any, and their available runs."""
        if not self._branches:
            return {}
        base = {branch: set() for branch in self._branches}
        for run, branches in self.runs.items():
            for branch in branches:
                base[branch].update({run})
        return base

    def _get_rundirs(
        self,
        branches: typing.Union[str, typing.Iterable[str]]=None,
    ) -> typing.List[pathlib.Path]:
        """Build an appropriate collection of runtime directories."""
        if not branches:
            return self.listing
        subset = (
            {branches} if isinstance(branches, str)
            else set(branches)
        )
        return [d for d in self.listing if d.parent.name in subset]

    @property
    def listing(self):
        """Full paths to all runtime directories.
        
        Notes
        -----
        This property does not use the `RunPaths.branches` property to iterate
        over available branches because that would create an infinite recursion
        via `RunPaths._get_rundirs`.
        """
        if self._listing is None:
            self._listing = [
                self.root / branch / self.base
                for branch in self._branches
            ] if self._branches else [self.root / self.base]
        return self._listing

    @property
    def root(self):
        """The root directory."""
        return self._root

    @property
    def base(self):
        """The name of the common base runtime directory."""
        return self._base


class Attrs:
    """A container for `Interface` attributes."""

    def __init__(self, path: paths.PathLike, **kwargs) -> None:
        root = paths.normalize(path)
        branches = tuple(kwargs.get('branches') or ())
        config = str(kwargs.get('config') or 'eprem.cfg')
        inputs = paths.localize(kwargs.get('inputs') or 'inputs')
        output = paths.localize(kwargs.get('output') or 'eprem.log')
        rundir = paths.localize(kwargs.get('rundir') or 'runs')
        logname = paths.localize(
            kwargs.get('logname') or 'runs'
        ).with_suffix('.json')
        self._public = {
            'root': root,
            'branches': branches,
            'config': config,
            'inputs': root / inputs,
            'output': output,
            'rundir': rundir,
            'logname': logname,
        }
        self._serial = None
        self._options = None

    @property
    def options(self):
        """The values of optional attributes."""
        if self._options is None:
            self._options = {
                k: v for k, v in self._public.items()
                if k != 'root'
            }
        return self._options

    @property
    def serial(self):
        """A serializable representation of this object."""
        if self._serial is None:
            self._serial = {
                k: self._serialize(v)
                for k, v in self._public.items()
            }
        return self._serial

    def _serialize(self, this):
        """Convert `this` to a serializable type."""
        if isinstance(this, pathlib.Path):
            return str(this)
        return this

    @property
    def root(self) -> pathlib.Path:
        """The project root directory."""
        return self._public['root']

    @property
    def branches(self) -> typing.Tuple[str]:
        """The distinct project branches, if any."""
        return self._public['branches']

    @property
    def config(self) -> str:
        """The name of the standard project configuration file."""
        return self._public['config']

    @property
    def inputs(self) -> pathlib.Path:
        """The project subdirectory containing configuration files."""
        return self._public['inputs']

    @property
    def output(self) -> pathlib.Path:
        """The local path component of the project output log."""
        return self._public['output']

    @property
    def rundir(self) -> pathlib.Path:
        """The local path component of the project run directory."""
        return self._public['rundir']

    @property
    def logname(self) -> pathlib.Path:
        """The local path component of the project log file."""
        return self._public['logname']

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        display = {k: v for k, v in self._public.items() if k != 'branches'}
        display['branches'] = self._public['branches'] or None
        return '\n'.join(f"{k}: {v}" for k, v in display.items())


InterfaceType = typing.TypeVar('InterfaceType', bound='Interface')


class Interface:
    """Interface to a group of EPREM runs."""

    def __init__(
        self,
        root: paths.PathLike,
        branches: typing.Iterable[str]=None,
        config: str=None,
        inputs: paths.PathLike=None,
        output: str=None,
        rundir: str=None,
        logname: str=None,
        copy: paths.PathLike=None,
    ) -> None:
        """Initialize a new project."""
        self._isvalid = False
        attrs = self._init_project(
            root,
            copy=copy,
            branches=branches,
            config=config,
            inputs=inputs,
            output=output,
            rundir=rundir,
            logname=logname,
        )
        self._log = None
        self._name = None
        self._root = None
        self._log = self._get_log(attrs)
        self._directories = RunPaths(attrs.root, attrs.branches, attrs.rundir)
        self._setup_cli(attrs)
        attrs.inputs.mkdir(parents=True, exist_ok=True)
        if copy:
            copied = self._restore_project(paths.normalize(copy))
            shutil.copytree(copied.inputs, attrs.inputs, dirs_exist_ok=True)
        self._attrs = attrs
        self._isvalid = True

    def _init_project(
        self,
        root: paths.PathLike,
        copy: paths.PathLike=None,
        **options,
    ) -> Attrs:
        """Initialize arguments from input or the database."""
        if not copy:
            return self._get_attrs(root, **options)
        restored = self._restore_project(paths.normalize(copy))
        copied = restored.options
        copied.update(options)
        return self._get_attrs(root, **copied)

    def _get_attrs(self, root: paths.PathLike, **options):
        """Create or restore project attributes."""
        path = paths.normalize(root)
        # If the project doesn't exist, create it.
        if not path.exists():
            return self._create_project(path, **options)
        # If the project exists and the user isn't attempting to overwrite it,
        # reinitialize the interface.
        if not options or all(v is None for v in options.values()):
            return self._restore_project(path)
        existing = (
            f"{self.__class__.__qualname__}"
            f"({os.path.relpath(path)!r})"
        )
        # If the project exists and the user is attempting to overwrite it,
        # raise an error.
        raise ProjectExistsError(
            f"The project {path.name!r} already exists in {path.parent}. "
            f"You can access the existing project via {existing}"
        )

    def _create_project(self, path: pathlib.Path, **options):
        """Set attributes on a new project."""
        attrs = Attrs(path, **options)
        attrs.root.mkdir(parents=True)
        with (path / '.eprem.conf').open('w') as fp:
            json.dump(attrs.serial, fp, indent=4, sort_keys=True)
        return attrs

    def _restore_project(self, path: pathlib.Path):
        """Load attributes of an existing project."""
        with (path / '.eprem.conf').open('r') as fp:
            old = dict(json.load(fp))
        here = old.pop('root')
        return Attrs(here, **old)

    def _get_log(self, attrs: Attrs):
        """Create or retrieve the log of runs."""
        path = attrs.root / attrs.logname
        if path.exists():
            return RunLog(path)
        return RunLog(
            path,
            config=attrs.config,
            output=attrs.output,
        )

    def _setup_cli(self, attrs: Attrs):
        """Make sure this project can run as a script."""
        path = attrs.root / '__main__.py'
        if path.exists():
            return
        with (DIRECTORY / '_project_main.py').open('r') as rp:
            lines = rp.readlines()
        payload = lines.copy()
        import_line = lines.index(f'import {__name__}\n')
        path_spec = (
            "import pathlib\n"
            "import sys\n"
            "\n"
            f"sys.path.append({str(DIRECTORY)!r})\n"
            "\n"
        )
        payload.insert(import_line, path_spec)
        with path.open('w') as wp:
            wp.writelines(payload)
            wp.write("if __name__ == '__main__':\n")
            wp.write("    cli.run()\n")
            wp.write("\n")
        if _HAVE_ISORT:
            isort.file(path, quiet=True)
        sys.path.append(attrs.root)

    def show(self: InterfaceType, *runs: str):
        """Display information about this project or the named run(s).
        
        Parameters
        ----------
        *runs : string
            The named run(s) to display. This method also accepts `'*'`, which
            will cause it to display information about all available runs.
        """
        if not runs:
            self._show_project()
        requested = (
            tuple(self.runs) if len(runs) == 1 and runs[0] == '*'
            else runs
        )
        for run in requested:
            etc.underline(run)
            self._show_run(run)

    def _show_project(self):
        """Display information about this project."""
        etc.underline("Project")
        print(self._attrs)
        if not self.branches:
            etc.underline("Runs")
            print('\n'.join(self.runs))
            return
        for branch, runs in self.branches.items():
            etc.underline(f"Branch {branch}")
            print('\n'.join(runs))

    def _show_run(self, run: str):
        """Display information about the named run."""
        try:
            branches = self.runs[run]
        except KeyError:
            print(f"No run named {run!r}")
            return
        for path in self.directories.resolve(run, branches):
            print(path)

    def reset(self, force: bool=False, silent: bool=False):
        """Reset this project to its initial state."""
        return self.rm('*', errors=(not force), silent=silent)

    def rename(self, target: str, force: bool=False, silent: bool=False):
        """Rename this project to `target`."""
        # Save the current root directory since it will change.
        old = self.root
        # Convert the target to a full path.
        new = paths.normalize(target)
        # Handle an existing target path.
        if new.exists():
            if not force:
                raise paths.PathOperationError(
                    f"Renaming this project to {target!r} would "
                    f"overwrite {new}."
                )
            if not silent:
                print(f"Overwriting {new}")
        # Update the runtime paths on disk.
        self._directories.update(root=new)
        # Update the log of runtime paths.
        self.log.update_directory(new)
        # Update the project metadata.
        self._update_metadata(str(old), str(new), new / '.eprem.conf')
        # Echo success, if applicable.
        if not silent:
            if self.root.parent == old.parent == pathlib.Path.cwd():
                result = target
            else:
                result = str(self.root)
            print(f"Renamed project to {result!r}")

    def _update_metadata(
        self,
        source: str,
        target: str,
        metadata: pathlib.Path,
    ) -> None:
        """Update this project's path-related metadata."""
        with metadata.open('r') as fp:
            current = dict(json.load(fp))
        updated = {k: v for k, v in current.items() if k != source}
        updated['root'] = target
        with metadata.open('w') as fp:
            json.dump(updated, fp, indent=4, sort_keys=True)
        with contextlib.suppress(ValueError):
            sys.path.remove(source)
        sys.path.append(target)

    def remove(self, force: bool=False, silent: bool=False):
        """Delete this project."""
        shutil.rmtree(self.root, ignore_errors=force)
        with contextlib.suppress(ValueError):
            sys.path.remove(str(self.root))
        self._isvalid = False
        if not silent:
            print(f"Removed project at {self.root}")

    def run(
        self: InterfaceType,
        config: paths.PathLike,
        name: str=None,
        branches: typing.Union[str, typing.Iterable[str]]=None,
        nproc: int=None,
        environment: typing.Dict[str, str]=None,
        errors: bool=False,
        silent: bool=False,
    ) -> InterfaceType:
        """Set up and execute a new EPREM run within this project."""
        run = name or datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S.%f')
        p = self.directories.mkdir(run, branches=branches)
        for path in p.errors(force=(not errors), silent=silent):
            self._create_run(
                config=config,
                path=path,
                nproc=nproc,
                environment=environment,
                silent=silent,
            )

    def _create_run(
        self: InterfaceType,
        config: paths.PathLike,
        path: pathlib.Path,
        nproc: int=None,
        environment: typing.Dict[str, str]=None,
        silent: bool=False,
    ) -> None:
        """Create a single run."""
        prjcfg = self.root / 'inputs' / config
        inputs = prjcfg if prjcfg.is_file() else paths.fullpath(config, strict=True)
        shutil.copy(inputs, path / self._attrs.config)
        branch = path.parent.parent
        mpirun = paths.locate('mpirun', branch, environment or {})
        eprem = paths.locate('eprem', branch, environment or {})
        command = (
            "nice -n 10 ionice -c 2 -n 3 "
            f"{mpirun} --mca btl_base_warn_component_unused 0 "
            f"-n {nproc or 1} {eprem} eprem.cfg"
        )
        output = path / self._attrs.output
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        with output.open('w') as stdout:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=path,
                stdout=stdout,
                stderr=subprocess.STDOUT,
            )
            if not silent:
                print(f"[{process.pid}]")
                print(f"Started {path.name!r} at {now}")
            process.wait()
            if not silent:
                base = f"Finished {path.name!r}"
                message = (
                    f"{base} in branch {branch.name!r}" if self.branches
                    else base
                )
                print(message)
        if process.returncode == 0:
            logentry = {
                'command': command,
                'time': now,
            }
            self.log.create(str(path), logentry)
        elif not silent:
            print(
                f"WARNING: Process exited with {process.returncode}",
                end='\n\n',
            )

    def mv(
        self: InterfaceType,
        source: str,
        target: str,
        branches: typing.Union[str, typing.Iterable[str]]=None,
        errors: bool=False,
        silent: bool=False,
    ) -> InterfaceType:
        """Rename an existing EPREM run within this project."""
        pairs = self.directories.mv(source, target, branches=branches)
        if not pairs:
            if not silent:
                print(f"Nothing to rename for {source!r}")
            return
        for (run, new) in pairs.errors(force=(not errors), silent=silent):
            self.log.mv(run, new)
            if not silent:
                branch = self._get_branch_name(run)
                base = f"Renamed {source!r} to {target!r}"
                print(f"{base} in branch {branch!r}" if branch else base)

    def rm(
        self: InterfaceType,
        run: str,
        branches: typing.Union[str, typing.Iterable[str]]=None,
        errors: bool=False,
        silent: bool=False,
    ) -> InterfaceType:
        """Remove an existing EPREM run from this project."""
        p = self.directories.rm(run, branches=branches)
        if not p:
            if not silent:
                print(f"Nothing to remove for {run!r}")
            return
        for path in p.errors(force=(not errors), silent=silent):
            self.log.rm(path)
            if not silent:
                base = f"Removed {path.name!r}"
                branch = self._get_branch_name(path)
                print(f"{base} from branch {branch!r}" if branch else base)

    def _get_branch_name(self, path: pathlib.Path):
        """Get the project branch name, if any, of `path`."""
        parents = (str(p) for p in path.relative_to(self.root).parents)
        with contextlib.suppress(StopIteration):
            if this := next(p for p in parents if p in self.branches):
                return this

    def _get_rundirs(
        self,
        branches: typing.Union[str, typing.Iterable[str]]=None,
    ) -> typing.List[pathlib.Path]:
        """Build an appropriate collection of runtime directories."""
        if not branches:
            return self.directories
        subset = (
            {branches} if isinstance(branches, str)
            else set(branches)
        )
        return [d for d in self.directories if d.parent.name in subset]

    @property
    def log(self):
        """The log of runs in this project."""
        return self._log

    @property
    def name(self):
        """The name of this project.
        
        This property is an alias for `~Interface.root.name`.
        """
        if self._name is None:
            self._name = self.root.name
        return self._name

    @property
    def runs(self):
        """The available runs, and owning branches, if any."""
        return self.directories.runs

    @property
    def branches(self):
        """The project branches, if any, and their available runs."""
        return self.directories.branches

    @property
    def root(self):
        """The top-level directory of this project."""
        return self.directories.root

    @property
    def directories(self):
        """The full path to each run directory."""
        return self._directories

    def __bool__(self) -> bool:
        """True if this is a valid project."""
        return self._isvalid

    def __eq__(self, other) -> bool:
        """True if two projects have the same initializing attributes."""
        if isinstance(other, Interface):
            return self._attrs == other._attrs
        return NotImplemented

    def __str__(self) -> str:
        """A simplified representation of this object."""
        return self.name

    def __repr__(self) -> str:
        """An unambiguous representation of this object."""
        return f"{self.__class__.__qualname__}({self.root})"


cli = interfaces.CLI(
    formatter_class=argparse.RawTextHelpFormatter,
    description=etc.doc2help(__doc__),
)


@cli.include
def create(
    path: paths.PathLike,
    branches: typing.Union[str, typing.Iterable[str]]=None,
    config: str=None,
    inputs: str=None,
    output: str=None,
    rundir: str=None,
    logname: str=None,
    copy: paths.PathLike=None,
    verbose: bool=False,
) -> None:
    """Create a new project."""
    project = Interface(
        path,
        branches=branches,
        config=config,
        inputs=inputs,
        output=output,
        rundir=rundir,
        logname=logname,
        copy=copy,
    )
    if verbose:
        parts = [
            f"Created project {project.name!r} in",
            f"{project.root.parent}",
        ]
        single = ' '.join(parts)
        message = single if len(single) < 70 else '\n'.join(parts)
        print(message)
cli.subcommands['create'].add_argument(
    'path',
    help="the path to the target project; may be relative",
)
cli.subcommands['create'].add_argument(
    '-b',
    '--branches',
    help="names of project branches\n(default: none)",
    nargs='*',
    metavar=('A', 'B'),
)
cli.subcommands['create'].add_argument(
    '-c',
    '--config',
    help=(
        "the name to give runtime config files"
        "\n(default: 'eprem.cfg')"
    ),
)
cli.subcommands['create'].add_argument(
    '-i',
    '--inputs',
    help=(
        "the name of the project subdirectory that will contain"
        "\nruntime configuration files"
        "\n(default 'inputs')"
    )
)
cli.subcommands['create'].add_argument(
    '-o',
    '--output',
    help=(
        "the name to give runtime output logs"
        "\n(default: 'eprem.log')"
    ),
)
cli.subcommands['create'].add_argument(
    '-d',
    '--rundir',
    help=(
        "the name of the directory that will contain simulation runs"
        "\n(default: 'runs')"
    ),
)
cli.subcommands['create'].add_argument(
    '-l',
    '--logname',
    help=(
        "the name of the file to which to log run metadata"
        "\n(default: 'runs.json')"
    ),
)
cli.subcommands['create'].add_argument(
    '--copy',
    help="create a copy of PROJECT",
    metavar='PROJECT',
)
cli.subcommands['create'].add_argument(
    '-v',
    '--verbose',
    help="print runtime messages",
    action='store_true',
)


@cli.include
def reset(
    path: paths.PathLike,
    force: bool=False,
    verbose: bool=False,
) -> None:
    """Reset an existing project."""
    project = Interface(path)
    project.reset(force=force, silent=(not verbose))
cli.subcommands['reset'].add_argument(
    'path',
    help="the path to the target project; may be relative",
)
cli.subcommands['reset'].add_argument(
    '-f',
    '--force',
    help="do not raise exceptions when resetting a project",
    action='store_true',
)
cli.subcommands['reset'].add_argument(
    '-v',
    '--verbose',
    help="print runtime messages",
    action='store_true',
)


@cli.include
def rename(
    path: paths.PathLike,
    target: paths.PathLike,
    force: bool=False,
    verbose: bool=False,
) -> None:
    """Rename an existing EPREM project."""
    project = Interface(path)
    project.rename(target, force=force, silent=(not verbose))
cli.subcommands['rename'].add_argument(
    'path',
    help="the path to the target project; may be relative",
)
cli.subcommands['rename'].add_argument(
    'target',
    help="the new name of the project",
)
cli.subcommands['rename'].add_argument(
    '-f',
    '--force',
    help="do not raise exceptions when renaming a project",
    action='store_true',
)
cli.subcommands['rename'].add_argument(
    '-v',
    '--verbose',
    help="print runtime messages",
    action='store_true',
)


@cli.include
def remove(
    path: paths.PathLike,
    force: bool=False,
    verbose: bool=False,
) -> None:
    """Remove an existing EPREM project."""
    project = Interface(path)
    project.remove(force=force, silent=(not verbose))
cli.subcommands['remove'].add_argument(
    'path',
    help="the path to the target project; may be relative",
)
cli.subcommands['remove'].add_argument(
    '-f',
    '--force',
    help="do not raise exceptions when a removing project",
    action='store_true',
)
cli.subcommands['remove'].add_argument(
    '-v',
    '--verbose',
    help="print runtime messages",
    action='store_true',
)


@cli.include
def show(
    path: paths.PathLike,
    runs: typing.Union[str, typing.Iterable[str]]=None,
) -> None:
    """Display information about an existing project."""
    project = Interface(path)
    project.show(*list(runs or []))
cli.subcommands['show'].add_argument(
    'path',
    help="the path to the target project; may be relative",
)
showruns = cli.subcommands['show'].add_mutually_exclusive_group()
showruns.add_argument(
    '-r',
    '--run',
    dest='runs',
    help=(
        "display information about the named run"
        ";\nspecify multiple times to include multiple runs"
    ),
    action='extend',
)
showruns.add_argument(
    '-a',
    '--all',
    dest='runs',
    help="display information for all runs",
    action='store_const',
    const='*',
)


if __name__ == '__main__':
    cli.run()

