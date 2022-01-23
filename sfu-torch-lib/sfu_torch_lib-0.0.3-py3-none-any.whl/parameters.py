import inspect
import sys
from typing import Callable, Union, Optional, List, Mapping, Set


PrimitiveType = Union[int, float, bool, str]


class ScriptParameters:
    @classmethod
    def get_positional_arguments(cls, argv: Optional[List[str]] = None) -> List[str]:
        argv = argv if argv else sys.argv[1:]

        arguments = []

        for argument in argv:
            if argument.startswith('-'):
                break

            arguments.append(argument)

        return arguments

    @classmethod
    def get_keyword_arguments(cls, argv: Optional[List[str]] = None) -> Set[str]:
        argv = argv if argv else sys.argv[1:]

        num_positional_arguments = len(cls.get_positional_arguments(argv))

        passed_arguments = {
            key.lstrip('-').replace('_', '-')
            for key in argv[num_positional_arguments::2]
            if key.startswith('-')
        }

        return passed_arguments

    @classmethod
    def get_script_parameters(
            cls,
            function: Callable,
            ignore_keyword_arguments: bool = True,
    ) -> Mapping[str, PrimitiveType]:
        """
        Returns the arguments of a function with its values specified by the command line or its default values.
        Underscores in the name of the arguments are transformed to dashes.
        Can optionally filter out keyword arguments obtained through the command line.
        :param function: the function to inspect.
        :param ignore_keyword_arguments: whether to filter out keyword command line arguments.
        :return: a map from argument names to default values.
        """
        positional_arguments, keyword_arguments = cls.get_positional_arguments(), cls.get_keyword_arguments()
        signature = inspect.signature(function)

        arguments = {}

        for index, (name, parameter) in enumerate(signature.parameters.items()):
            transformed_name = name.replace('_', '-')

            if index < len(positional_arguments):
                arguments[transformed_name] = positional_arguments[index]

            elif not (ignore_keyword_arguments and transformed_name in keyword_arguments):
                if parameter.default != parameter.empty:
                    arguments[transformed_name] = parameter.default

        return arguments
