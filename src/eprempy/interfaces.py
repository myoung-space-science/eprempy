import argparse
import functools
import types
import typing

from . import etc


class CLI(typing.Mapping):
    """A custom command-line parser for EPREM simulations."""

    def __init__(self, *args, **kwargs):
        """Create a new instance."""
        self._args = args
        self._kwargs = kwargs
        self._parser = argparse.ArgumentParser(*self._args, **self._kwargs)
        self._subparsers = None
        self._subcommands = None

    def __len__(self) -> int:
        """Called for len(self)."""
        return len(self.subcommands)

    def __iter__(self) -> typing.Iterator[str]:
        """Called for iter(self)."""
        return iter(self.subcommands)

    def __getitem__(self, __k: str) -> argparse.ArgumentParser:
        """Access subcommands by key."""
        if __k in self.subcommands:
            return self.subcommands[__k]
        raise KeyError(f"No subcommand for {__k!r}")

    def include(self, _func=None, **meta):
        """Register a subcommand."""
        def cli_action(func: types.FunctionType):
            """Decorate `func` as a command-line action."""
            key = func.__name__
            subparser = self.subparsers.add_parser(
                key,
                help=etc.doc2help(func),
                description=etc.doc2help(func),
                formatter_class=argparse.RawTextHelpFormatter,
                **meta
            )
            subparser.set_defaults(func=func)
            self.subcommands[key] = subparser
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        if _func is None:
            return cli_action
        return cli_action(_func)

    def run(self):
        """Execute operations based on command-like arguments."""
        parsed = vars(self.parser.parse_args())
        func = parsed.pop('func')
        func(**parsed)

    @property
    def parser(self):
        """The main argument parser."""
        return self._parser

    @property
    def subparsers(self):
        """The parser for each subcommand."""
        if self._subparsers is None:
            self._subparsers = self.parser.add_subparsers(
                title="supported sub-commands",
            )
        return self._subparsers

    @property
    def subcommands(self) -> typing.Dict[str, argparse.ArgumentParser]:
        """The registered subcommands."""
        if self._subcommands is None:
            self._subcommands = {}
        return self._subcommands


