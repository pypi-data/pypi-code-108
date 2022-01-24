"""Show public transport times."""

import sys
from hsltimes import argparser


__program__: str = "hsltimes"
__author__: str = ""
__copyright__: str = ""
__credits__: list = ["Niklas Larsson", "Ben Panyanil"]
__license__: str = ""
__version__: str = "0.0.1b0"
__maintainer__: str = ""
__email__: str = ""
__status__: str = ""


def main(argc: int=len(sys.argv), argv: list=sys.argv) -> None:
    """Main function."""
    parser: object = argparser.ArgumentParser(argv, __program__)
    parser.parse_args()

    if parser.help:
        print(f"Usage: {__program__} [OPTIONS]")
        print()
        print(f"{__doc__}")
        print()
        print("Options:")
        print("  -h,  --help.......... Print this message and exit.")
        print(f"  -V,  --version....... Print {__program__} version and exit.")
        print("  -A,  --authors....... Print authors and exit.")
        sys.exit(0)

    if parser.version:
        print(f"{__program__}, {__version__}")
        sys.exit(0)

    if parser.authors:
        for i in __credits__:
            print(i)
        del i
        sys.exit(0)


if __name__ == "__main__":
    main()
