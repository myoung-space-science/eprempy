import argparse

from . import cli
from . import parameter


def print_version():
    from importlib.metadata import version
    print(f"{__package__} {version(__package__)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog=__package__,
        description="Command-line interface for EPREM Python utilities",
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
    configfile_parser = subparsers.add_parser(
        'configfile',
        description=cli.DESCRIPTIONS['configfile'],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="utilities for EPREM runtime configuration files",
    )
    configfile_parser.add_argument(
        '-s', '--source',
        help=(
            "use source code in SRC for default parameter values"
            f"; otherwise, use the {__package__} database of default values"
        ),
        metavar='SRC',
    )
    configfile_mode = configfile_parser.add_mutually_exclusive_group(
        required=True,
    )
    configfile_mode.add_argument(
        '-g', '--generate',
        help="create a configuration file from default values",
        metavar='FILE',
    )
    configfile_mode.add_argument(
        '-c', '--compare',
        dest='files',
        help="compare values in the configuration file(s) to default values",
        nargs='+',
        metavar=('FILE0', 'FILE1'),
    )
    configfile_parser.add_argument(
        '-v', '--verbose',
        help="(generate) print status messages",
        action='store_true',
    )
    configfile_parser.add_argument(
        '--diff',
        help="(compare) show only parameters with differing values",
        action='store_true',
    )
    configfile_parser.add_argument(
        '--names',
        help="(compare) show full file names",
        action='store_true',
    )
    options = vars(parser.parse_args())
    if options.pop('version', None):
        print_version()
    elif usermode := options.pop('mode'):
        try:
            cli.run(usermode, options)
        except cli.UserError as err:
            print()
            print(f"ERROR: {err}")
            print(f"       Try 'python -m {__package__} {usermode} --help'")
    else:
        parser.error(f"No arguments. Try 'python -m {__package__} --help'")

