""" Parse parameters set with --set """
from mdpeditor.mdpblocks import provide
from configparser import ParsingError


def parse_set_parameters(set_value):
    try:
        set_values_as_mdp_string = "\n".join(set_value)
        return provide.mdp_string_to_ordered_dict(set_values_as_mdp_string)
    except ParsingError:
        set_value_as_string = "\n".join(set_value)
        raise SystemExit(f'Cannot parse the parameters you are trying to '
                         f'set with --set {set_value_as_string}.'
                         f'\nDid you use this format:\t'
                         f'--set key=value ?')
