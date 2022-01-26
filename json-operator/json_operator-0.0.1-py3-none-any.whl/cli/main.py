import argparse
import json
import sys
from inspect import getmembers, isfunction
import json_operator


_operations = getmembers(json_operator, isfunction)
_op_keys = list(k for k,v in _operations)
_op_map = {k:v for k,v in _operations}


def _get_parser():
    parser = argparse.ArgumentParser(add_help=False,
        description='command utility to operate on JSON objects. Supported operators: %s.' % ", ".join(_op_keys))
    parser.add_argument('operator', nargs='?', action='store', help='action command')
    parser.add_argument('--lt', action='store', help='left-side JSON text. Overwrite --lf option')
    parser.add_argument('--rt', action='store', help='right-side JSON text. Overwrite --rf option')
    parser.add_argument('--lf', action='store', help='left-side file where JSON is stored')
    parser.add_argument('--rf', action='store', help='right-side file where JSON is stored')
    parser.add_argument("--out", action='store', help='output file. Default is stdout')
    parser.add_argument('--help', action='help', help='print this help message')
    return parser


def _get_json(f, text):
    if text:
        return json.loads(text)
    with open(f, "r") as fh:
        data = fh.read()
    return json.loads(data)


def main():
    parser = _get_parser()
    args = parser.parse_args(sys.argv[1:])
    if hasattr(args, "help") and args.help:
        parser.print_usage()
        return 0
    if args.operator not in _op_map:
        print("Invalid operator. Use --help to check help menu. Supported operators are: %s" % ", ".join(_op_keys))
        return 1
    if not args.lt and not args.lf:
        print("No left-side JSON, use --lt or --lf")
        return 1
    if not args.rt and not args.rf:
        print("No right-side JSON, use --rt or --rf")
        return 1
    left = _get_json(args.lf, args.lt)
    right = _get_json(args.rf, args.rt)
    res = _op_map[args.operator](left, right)
    data = json.dumps(res)
    if args.out:
        with open(args.out, "wt") as f:
            f.write(data)
    else:
        print(data)


if __name__ == "__main__":
    main()
