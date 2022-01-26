from __future__ import annotations

import argparse
import sys

from fakelish import fakelish


def main():
    """English-like word generator"""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--min", type=int, dest="min_length", default=6, help="min length of fake word"
    )
    parser.add_argument(
        "--max", type=int, dest="max_length", default=9, help="max length of fake word"
    )
    parser.add_argument(
        "-n",
        "--n-words",
        dest="n_words",
        type=int,
        default=10,
        help="number of fake words (negative makes infinite)",
    )
    parser.add_argument(
        "--no-capitalize",
        dest="capitalize",
        action="store_false",
        help="do not capitalize the first letter",
    )
    args = parser.parse_args()

    if args.n_words < 0:
        args.n_words = sys.maxsize ** 10
    for i in range(args.n_words):
        fake_word = fakelish.generate_fake_word(args.min_length, args.max_length)
        if args.capitalize:
            fake_word = fake_word.capitalize()
        sys.stdout.write(f"{fake_word}\n")
