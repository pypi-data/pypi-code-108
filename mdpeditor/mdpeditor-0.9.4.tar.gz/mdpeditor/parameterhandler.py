""" handle parameters like transforming, merging, converting"""
from dataclasses import dataclass

from collections import OrderedDict
import mdpeditor.mdpblocks.provide


@dataclass
class CompiledParameters:

    """The result of compiling parameters,
       keeping track of meta during the compilation process like key duplications
    """
    parameters: OrderedDict
    duplicate_keys: set


def compile_parameters(option_blocks):

    """merge block by block into parameters, keeping track of duplicates

    Args:
        option_blocks (iterable over OrderedDict): Options to merge
    """

    parameters = OrderedDict()  # type: OrderedDict
    duplicate_keys = set()

    for block in option_blocks:

        # collect overlapping parameters in the blocks
        duplicate_keys |= set(parameters.keys()) & set(block.keys())
        parameters.update(block)

    return CompiledParameters(parameters, duplicate_keys)


class OutputParameters:
    """
    Handle parameter output like printing and cleaning
    """
    def __init__(self, parameters):

        # open default .mdp and fill in the "other parameters"
        # discard all non-default parameters
        self.parameters = mdpeditor.mdpblocks.provide.default_parameter_block()

        for key in self.parameters.keys():
            if key in parameters.keys():
                self.parameters[key] = parameters[key]

    def keep_only(self, keys_to_keep):
        """ Remove all keys that are not to be kept """
        keys_to_pop = [key for key in self.parameters.keys() if key not in keys_to_keep]
        for key in keys_to_pop:
            self.parameters.pop(key)

    def as_string(self):
        """ write the parameters as a string in .mdp format"""
        max_key_length = max(map(len, self.parameters.keys()))

        formatted_mdp_entries = [
            f'{key:{max_key_length+1}s} = {value}'
            for key, value in self.parameters.items()
        ]

        return '\n'.join(formatted_mdp_entries) + "\n"

    def as_colored_string(self, keys_to_color):
        """ write the parameters as a string in .mdp format"""
        max_key_length = max(map(len, self.parameters.keys()))
        color = "\u001b[32m"  # green
        reset = "\u001b[0m"

        formatted_mdp_entries = [
            f'{color}{key:{max_key_length+1}s} = {value}{reset}'
            if key in keys_to_color else f'{key:{max_key_length+1}s} = {value}'
            for key, value in self.parameters.items()
        ]

        return '\n'.join(formatted_mdp_entries) + "\n"
