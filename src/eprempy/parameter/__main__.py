"""
The command-line interface (CLI) for this module.
"""

import argparse

from ._interface import (
    DB_PATH,
    DESCRIPTIONS,
    run,
)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate or compare EPREM configuration files.",
        formatter_class=argparse.RawTextHelpFormatter,
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
    cli = vars(parser.parse_args())
    usermode = cli.pop('mode')
    run(usermode, cli)

