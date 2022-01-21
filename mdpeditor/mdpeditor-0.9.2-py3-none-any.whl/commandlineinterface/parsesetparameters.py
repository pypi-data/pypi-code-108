""" Parse parameters set with --set """
from mdpeditor.mdpblocks import provide
from configparser import ParsingError

def parse_set_parameters(set_value):
    try:
        set_values_as_mdp_string = "\n".join(set_value)
        return provide.mdp_string_to_ordered_dict(set_values_as_mdp_string)
    except ParsingError:
        raise SystemExit("Cannot parse the parameters you are trying to "
                         "set with --set.\nDid you use this format:\t"
                         "--set key=value ?")
