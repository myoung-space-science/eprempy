# Example CLI Commands

The `eprempy` package may be run as a command-line interface (CLI). Under the hood, this works because it defines `__main__.py`, but the underlying details are not important here. This document describes some basic uses of that CLI. 

Show the top-level help message.
```shell
python -m eprempy -h
```
or
```shell
python -m eprempy --help
```

Compare simulation configuration files.
```shell
python -m eprempy compare [OPTIONS]
```

Generate default parameter values.
```shell
python -m eprempy generate [OPTIONS]
```

Note that all subcommands (e.g., `compare`) also support the `-h/--help` option.


