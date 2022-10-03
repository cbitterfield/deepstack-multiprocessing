from os import getcwd
import argparse
from pprint import pprint


def cli(**kwargs):
    """
    This function is used to execute the CLI command.

    :param version: The version number
    :param program_name: The name of the program
    :param description: The description of the program
    :param debug: The standard debug levels (debug, info, warn) debug is panic


    :type kwargs:
    :return:
    :rtype: namespace
    """
    debug = kwargs.get('debug', False)
    description = kwargs.get('description', None)
    version = kwargs.get('version', None)
    program_name = kwargs.get('program', None)
    epilog = kwargs.get('epilog', None)

    if debug:
        print("CLI Arguments")
        pprint(kwargs)


    parser = argparse.ArgumentParser()
    parser.prog = program_name
    parser.description = description
    parser.epilog = epilog

    # Defaults for all programs
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + version)

    parser.add_argument('--debug',
                        help='Turn on Debugging Mode',
                        type=str,
                        action='store',
                        required=False,
                        dest='debug',
                        default="INFO"
                        )

    parser.add_argument('-d', '--directory)',
                        help='The directory for all movies to search',
                        type=str,
                        action='store',
                        required=True,
                        dest='search_directory',
                        default=getcwd()
                        )

    parser.add_argument('-o', '--output)',
                        help='The directory for headshots',
                        type=str,
                        action='store',
                        required=True,
                        dest='output',
                        default=getcwd()
                        )

    parser.add_argument('-l', '--logfile)',
                        help='Default is to write the log to the local directory',
                        type=str,
                        action='store',
                        required=False,
                        dest='logfile',
                        default=getcwd() + program_name + ".log"
                        )


    parser.add_argument('-s', '--studio_name',
                        help='Append the studio name to all movies',
                        type=str,
                        action='store',
                        required=False,
                        dest='studio_name',
                        default=""
                        )

    parser.add_argument('--test',
                        help='''Output the FFmpeg commands aka compile but take no action to write''',
                        action='store_true',
                        required=False,
                        dest='test',
                        default=False
                        )

    parser.add_argument('--database',
                        help='''Write each file and its information to a SQLite3 database if not set, output is only
                        to the log file.''',
                        action='store',
                        required=False,
                        dest='database',
                        default=False
                        )

    parser.add_argument('--path-start',
                        help='''Remove this from the stored path to provide a cleaner database.''',
                        action='store',
                        required=False,
                        dest='path_start',
                        default=False
                        )

    parser.add_argument('--resume',
                        help='''Resume after this directory''',
                        type=str,
                        action='store',
                        required=False,
                        dest='resume',
                        default=None
                        )

    parser.add_argument('--run-one',
                        help='''Run one directory as a test''',
                        type=str,
                        action='store',
                        required=False,
                        dest='run_one',
                        default=None
                        )

    parser.add_argument('--stop-after',
                        help='''Stop After x number of files''',
                        type=int,
                        action='store',
                        required=False,
                        dest='stop_after',
                        default=200000
                        )

    parser.add_argument('--confidence',
                        help='''Face recognition min confidence''',
                        type=float,
                        action='store',
                        required=False,
                        dest='confidence',
                        default=.72
                        )

    parser.add_argument('--workers',
                        help='''Face recognition min confidence''',
                        type=int,
                        action='store',
                        required=False,
                        dest='workers',
                        default=10
                        )

    parse_out = parser.parse_args()
    return parse_out
