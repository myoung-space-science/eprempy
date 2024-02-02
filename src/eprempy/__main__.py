import argparse

from .parameter._interface import (
    run,
    DESCRIPTIONS,
    DB_PATH,
    UserError,
)


def print_version():
    from importlib.metadata import version
    print(f"eprempy {version('eprempy')}")


if __name__ == '__main__':
    replacements = {
        '`src`': 'SRC',
        '`source`': 'SRC',
        "`paths`": "the given paths",
        '`': "'",
        "the local database": DB_PATH,
    }
    parser = argparse.ArgumentParser(
        prog='eprempy',
        description="Generate or compare EPREM configuration files.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '-V', '--version',
        help="print the current package version",
        action='store_true',
    )
    subparsers = parser.add_subparsers(
        title="modes",
        dest="mode",
    )
    database_parser = subparsers.add_parser(
        'database',
        description=DESCRIPTIONS['database'],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="generate database of default parameter values",
    )
    database_parser.add_argument(
        '-s', '--source',
        help="use files in SRC to define default parameter values",
        metavar='SRC',
    )
    database_parser.add_argument(
        '--append',
        help=(
            "append parameters to the existing database"
            f"; otherwise, overwrite {DB_PATH}"
        ),
        action='store_true',
    )
    database_parser.add_argument(
        '-v', '--verbose',
        help="print informational messages",
        action='store_true',
    )
    parameters_parser = subparsers.add_parser(
        'parameters',
        description=DESCRIPTIONS['parameters'],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="compare parameter values",
    )
    parameters_parser.add_argument(
        '-c', '--compare',
        dest='files',
        help="one or more configuration files to view",
        nargs='+',
        metavar=('FILE0', 'FILE1'),
    )
    parameters_parser.add_argument(
        '-s', '--source',
        help=(
            "use files in SRC when showing default parameter values"
            f"; otherwise, use definitions in {DB_PATH}"
        ),
        metavar='SRC',
    )
    parameters_parser.add_argument(
        '--diff',
        help=(
            "show only parameters with differing values"
            "; otherwise, show all parameters"
        ),
        action='store_true',
    )
    parameters_parser.add_argument(
        '--names',
        help="show full file names",
        action='store_true',
    )
    cli = vars(parser.parse_args())
    if cli.pop('version', None):
        print_version()
    elif usermode := cli.pop('mode'):
        try:
            run(usermode, cli)
        except UserError as err:
            print()
            print(f"ERROR: {err}")
            print(f"       Try running 'python -m eprempy {usermode} -h'")
    else:
        parser.error("No arguments. Try 'eprempy -h' for more information.")

