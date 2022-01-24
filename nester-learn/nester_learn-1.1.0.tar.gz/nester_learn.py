"""
This is the “nester_learn.py" module, and it provides one function called
print_nested_lists() which prints lists that may or may not include nested lists.
"""


def print_nested_lists(inp_list, level):
    """ Prints each item from a nested list
    :param inp_list: any list (maybe nested)
    :param level: number of tabs between nested lists
    """
    for item in inp_list:
        if isinstance(item, list):
            print_nested_lists(item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(item)
