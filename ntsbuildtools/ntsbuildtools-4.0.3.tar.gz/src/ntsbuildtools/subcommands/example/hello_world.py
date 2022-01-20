"""Simple Hello World functionality."""
from configargparse import ArgParser

def config_parser(parser: ArgParser):
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help="Be extra verbose when saying 'hello world!'")

def main(args):
    if args.verbose:
        print("With all the verbosity in the world... Hello World!")
    else:
        print("Hello World!")
