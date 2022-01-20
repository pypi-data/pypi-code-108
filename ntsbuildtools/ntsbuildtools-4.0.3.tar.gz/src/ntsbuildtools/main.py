import sys

import ntsbuildtools.cli
import ntsbuildtools.subcommands


def main():
    ntsbuildtools.cli.set_version(ntsbuildtools.__version__)
    ntsbuildtools.cli.register(ntsbuildtools.subcommands)
    enable_argcomplete_autocomplete(ntsbuildtools.cli.get_parser())
    ntsbuildtools.cli.run(sys.argv[1:])


def enable_argcomplete_autocomplete(parser):
    """Enable command-line interface tab-autocompletion via the argcomplete package.

    If the argcomplete package is not available, this will do nothing.

    Args:
        parser (ArgumentParser): The argument parser to configure for tab-completion.
    """
    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass


if __name__ == '__main__':
    main()
