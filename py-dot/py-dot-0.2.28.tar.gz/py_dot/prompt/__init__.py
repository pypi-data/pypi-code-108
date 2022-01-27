import getopt
import sys
from typing import List, Dict


def get_command_values(long_names: List[str]) -> Dict:
    """ Get Command Arguments as Optional

    `getopt` cannot ignore optional argument, then Use this.

    :param long_names: parameter name starts without '--'
    :return:
    """
    argv = sys.argv[1:]

    values = {}

    space_long_name = False
    for arg_value in argv:
        if arg_value[0:2] != '--':
            if space_long_name:
                if space_long_name in values:
                    value = values[space_long_name]
                    if isinstance(value, list):
                        value.append(arg_value)
                    else:
                        values[space_long_name] = [value, arg_value]
                else:
                    values[space_long_name] = arg_value
            continue

        space_long_name = False
        current = 0
        for long_name in long_names:
            if arg_value.startswith(long_name + '=', 2):
                value = arg_value[len(long_name) + 3:]
                values[long_name] = value

                if not long_names:
                    return values

                break

            if arg_value.startswith(long_name, 2):
                long_names.pop(current)
                space_long_name = long_name

                break

            current += 1

    return values
