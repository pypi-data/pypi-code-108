import argparse
from .util import *


def main():
    parser = argparse.ArgumentParser(description="Juggling with hex")
    parser.add_argument("input", help="Input")
    parser.add_argument("-r", action="store_true", help="reverse")
    parser.add_argument("-o", action="store_true", help="octal mode")
    args = parser.parse_args()

    print(
        (from_oct(args.input) if args.o else from_hex(args.input))
        if args.r
        else (normalize_to_oct(args.input) if args.o else normalize_to_hex(args.input))
    )


if __name__ == "__main__":
    main()
