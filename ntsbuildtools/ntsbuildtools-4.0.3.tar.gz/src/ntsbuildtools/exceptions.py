"""All of the custom Errors that BuildTools 
"""
from textwrap import dedent

class BTError(Exception):
    """The base class for all BuildTools errors."""
    pass


class BTConventionError(BTError):
    """Errors that will be thrown if the BuildTools `subcommands` package breaks 
    any of the conventions outlined in our "CLI Framework" documentation. 
    """
    pass


class BTMainFuncMissingError(BTConventionError):
    def __init__(self, module_name):
        message = dedent(f"""\
            module {module_name} is missing its 'main' method! 
            Each module in the subcommands package must define a 'main(args)' function.
            """)
        super().__init__(message)


class BTConfigParserSignatureError(BTConventionError):
    def __init__(self, module_name):
        message = dedent(f"""\
            module {module_name} has the incorrect arguments for its 'config_parser' function! 
            The signature should be `def config_parser(parser: configargparse.ArgParser)`.
            """)
        super().__init__(message)


class BTMainFuncSignatureError(BTConventionError):
    def __init__(self, module_name):
        message = dedent(f"""\
            module {module_name} has the incorrect arguments for its 'main' function! 
            The signature should be `def main(args: configargparse.Namespace)`.
            """)
        super().__init__(message)


class BTTeamsCardFactoryError(BTError):
    pass
