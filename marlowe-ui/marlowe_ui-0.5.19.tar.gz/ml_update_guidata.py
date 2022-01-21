import sys
import argparse
import json

from marlowe_ui import guidata

parser = argparse.ArgumentParser()

parser.add_argument('input', nargs='?', type=argparse.FileType('r'),
                    default=sys.stdin, help='json input')
parser.add_argument('output', nargs='?', type=argparse.FileType('w'),
                    default=sys.stdout, help='json output')
parser.add_argument('--verbose', '-v', action='store_true', default=False,
                    help='verbose output')

args = parser.parse_args()

din = json.load(args.input)

if args.verbose:
    print('input version:', guidata.getversion(din), file=sys.stderr)
dout = guidata.solve_version(din)

if args.verbose:
    print('output version:', guidata.getversion(dout), file=sys.stderr)

json.dump(dout, args.output)
