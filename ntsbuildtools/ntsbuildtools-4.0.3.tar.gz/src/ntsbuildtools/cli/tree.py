import inspect
import sys
from typing import List, Callable

import anytree
import configargparse

import ntsbuildtools.exceptions


class ArgParserNode(anytree.NodeMixin):
    """A Tree data structure for building an ArgParser with many subcommands.
    """
    def __init__(self, command: str, 
                 parser: configargparse.ArgumentParser, 
                 parent: 'ArgParserNode' = None, 
                 children: List['ArgParserNode'] = None):
        self._command = command
        self._parser = parser
        self.parent = parent
        if children:
            self.children = children
        self._subparser_factory = None

    @property
    def command(self):
        return self._command

    def _create_subparser_factory(self):
        """Creating a subparser requires tracking a 'subparser action object' -- we refer to this
        as the 'subparser_factory.' This method creates and configures that 'subparser action object'.
        """
        if sys.version_info.minor >= 7:
            self._subparser_factory = self._parser.add_subparsers(
                required=True, 
                dest="subcommand", 
                parser_class=configargparse.ArgParser
            )
        else:  # Python 3.6 support: 'required=True' argument may cause TypeError.
            self._subparser_factory = self._parser.add_subparsers(
                dest="subcommand", 
                parser_class=configargparse.ArgParser
            )
            self._subparser_factory.required = True

    @staticmethod
    def _sanitize_subcommand(subcommand: str):
        """Clean up any characters from the subcommand that does not meet our naming convention.

        Args:
            subcommand (str): The subcommand to be cleaned/checked.

        Returns:
            str: The subcommand without any invalid characters
        """
        return subcommand.replace('_','-')

    def _add_subparser(self, subcommand, help_msg):
        """Add a subparser to this node's (private) ArgumentParser, and return it. This
        is a wrapper to simplify interfacing with ArgumentParser's `add_subparsers` method.

        Args:
            subcommand (str): The name of the subcommand/subparser to be added.
            help_msg (str): The help message 

        Returns:
            configargparse.ArgumentParser: The subparser!
        """
        if self._subparser_factory is None:
            self._create_subparser_factory()
        return self._subparser_factory.add_parser(subcommand, help=help_msg)

    def add(self, subcommand: str, help_msg: str) -> 'ArgParserNode':
        """Add a subcommand directly to this Node. This is generally used for adding intermediate
        subcommands that do not have a `default_func` associated with them.

        Args:
            subcommand (str): The name of the subcommand to be added to the CLI. Any underscores 
                              will be replaced with hyphens.
            help_msg (str): The help message that will show in the CLI for this subcommand.

        Returns:
            ArgParserNode: The added node.

        Example:
            Adding an inner 'example' CLI path: "buildtools example". This is the first step
            to creating a subcommand with an actual default_func, where the functionality
            lies. See `ArgParserNode.add_leaf()` for more information.


                Setup the "Root ArgParser" and the Tree data structure.
                >>> _root_parser = configargparse.ArgumentParser()
                >>> tree_root = ArgParserNode(command='buildtools', parser=_root_parser)

                Add the 'example' subcommand node!
                >>> tree_root.add('example', 'Just some example subcommands.')
                ArgParserNode(command='example')
            """
        subcommand = ArgParserNode._sanitize_subcommand(subcommand)
        new_child_parser = self._add_subparser(subcommand, help_msg)
        child_node = ArgParserNode(parser=new_child_parser, command=subcommand, parent=self)
        return child_node

    def add_leaf(self, subcommand: str, help_msg: str, default_func: Callable[[configargparse.Namespace],None], 
                 config_parser: Callable[[configargparse.ArgumentParser],None] = None) -> 'ArgParserNode':
        """Add a leaf node -- the leaf *must* provide a `default_func` Callable. 
        Additionally, the `config_parser` Callable may be provided, e.g. if your default_func 
        has any parameters (see the example).

        The leaf nodes are where the true functionality of the CLI is provided. The leaf nodes
        hold onto the 'default functions' which are the actual 'subcommands' provided in the
        `subcommands` package.

        Implementation Note: The `default_func` is assigned using a pattern discussed in `argparse` documentation.


        Args:
            subcommand (str): The name of the leaf-subcommand to be added. Any underscores 
                              will be replaced with hyphens.
            help_msg (str): The help message that will show in the CLI for this subcommand.
            default_func (Callable): The default function -- effectively the 'main' function 
                that corresponds to this subcommand.
            config_parser (Callable[[configargparse.ArgumentParser], None]): If the default 
                function requires any parameters, those should be configured via this  
                Callable (see the example).

        Returns:
            ArgParserNode: The added node.

        Example:
            Adding a "Hello, {Your name here}!" functionality. This has the CLI arguments 
            like: "hello <name>".

                Setup the "Root ArgParser" and the Tree data structure.
                >>> _root_parser = configargparse.ArgumentParser()
                >>> _tree_root = ArgParserNode(command='buildtools', parser=_root_parser)

                Add the 'hello' subcommand -- including Callables!
                >>> def config_parser_for_hello_function(parser):
                ...    parser.add_argument('name')
                >>> def hello_function(args):
                ...    print(f"Hello, {args.name}!")
                >>> _tree_root.add_leaf('hello', "Just some basic 'hello, world!' functionality", 
                ...     hello_function, config_parser_for_hello_function)
                ArgParserNode(command='hello')

                Parse arguments
                >>> parsed_args = _root_parser.parse_args(['hello', 'Fred'])

                This will execute `hello_function` (with args.name = 'Fred')
                >>> parsed_args.func(parsed_args)
                Hello, Fred!
        """
        child_node = self.add(subcommand, help_msg)
        child_node.set_default_func(default_func)
        if config_parser:
            child_node.config_parser(config_parser)
        return child_node

    def config_parser(self, config_parser_func: Callable[[configargparse.ArgumentParser], None]):
        """Configure the parser that is stored in this node.

        Args:
            config_parser (Callable): A callable that will configure this ArgParserNode's internal ArgumentParser.
        """
        if list(inspect.signature(config_parser_func).parameters) != ["parser"]:
            raise ntsbuildtools.exceptions.BTConfigParserSignatureError(config_parser_func.__module__)
        config_parser_func(self._parser)

    def set_default_func(self, default_func: Callable):
        """Provide the 'main' functionality of this particular ArgParserNode.

        Args:
            default_func (Callable): The default function for this ArgParser -- effectively the 
                'main' function that corresponds to this subcommand.

        Raises:
            BTMainFuncSignatureError: If the default_func parameters do not match our convention.
        """
        if list(inspect.signature(default_func).parameters) != ["args"]:
            raise ntsbuildtools.exceptions.BTMainFuncSignatureError(default_func.__module__)
        self._parser.set_defaults(func=default_func)

    def __repr__(self):
        return f"ArgParserNode(command='{self._command}')"
