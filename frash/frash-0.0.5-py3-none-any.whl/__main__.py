import argparse
from .util import *


def main():
    parser = argparse.ArgumentParser(description="Juggling with hex")
    parser.add_argument("input", help="Input")
    parser.add_argument("-r", action="store_true", help="reverse")
    args = parser.parse_args()

    if args.r:
        print(from_hex(args.input))
    else:
        output = normalize_to_hex(args.input)
        print(output)


if __name__ == "__main__":
    main()
