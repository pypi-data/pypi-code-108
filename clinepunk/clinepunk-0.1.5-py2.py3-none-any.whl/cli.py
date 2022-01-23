"""Console script for clinepunk."""
import sys

import click

from clinepunk import clinepunk


@click.command()
def main(args=None):
    """Console script for clinepunk."""
    words = clinepunk.get_words(count=2)
    out = "".join(words)
    print(out)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


if __name__ == "__main__":
    main()
