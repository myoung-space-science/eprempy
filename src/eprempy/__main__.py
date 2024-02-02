import argparse

from . import cli
from . import parameter


def print_version():
    from importlib.metadata import version
    print(f"eprempy {version('eprempy')}")


if __name__ == '__main__':
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
    parameters_parser = subparsers.add_parser(
        'parameters',
        description=cli.DESCRIPTIONS['parameters'],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="compare parameter values",
    )
    parameters_parser.add_argument(
        '-s', '--source',
        help=(
            "use files in SRC for default parameter values"
            f"; otherwise, use definitions in {parameter.DB_PATH}"
        ),
        metavar='SRC',
    )
    parameters_mode = parameters_parser.add_mutually_exclusive_group(
        required=True,
    )
    parameters_mode.add_argument(
        '-g', '--generate',
        help="create a configuration file from default values",
        metavar='FILE',
    )
    parameters_mode.add_argument(
        '-c', '--compare',
        dest='files',
        help="compare values in the configuration file(s) to default values",
        nargs='+',
        metavar=('FILE0', 'FILE1'),
    )
    parameters_parser.add_argument(
        '-v', '--verbose',
        help="(generate) print status messages",
        action='store_true',
    )
    parameters_parser.add_argument(
        '--diff',
        help="(compare) show only parameters with differing values",
        action='store_true',
    )
    parameters_parser.add_argument(
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
            print(f"       Try running 'python -m eprempy {usermode} -h'")
    else:
        parser.error("No arguments. Try 'eprempy -h' for more information.")

