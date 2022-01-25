"""flower_box.py module.

==========
flower_box
==========

With **print_flower_box_msg** you can print messages in a flower_box,
meaning a box of asterisks.

:Example: print a one line message in a flower box

>>> from scottbrian_utils.flower_box import print_flower_box_msg
>>> print_flower_box_msg('This is my message to the world')
<BLANKLINE>
***********************************
* This is my message to the world *
***********************************

"""

from typing import Any, List, Union


def print_flower_box_msg(msgs: Union[str, List[str]],
                         **kwargs: Any) -> None:
    """Print a single or multi-line message inside a flower box.

    Args:
        msgs: single message or list of messages to print
        kwargs: Specifies the print arguments to use on the print
                  statement, such as *end*, *file*, or *flush*.

    :Example: print a two line message in a flower box

    >>> from scottbrian_utils.flower_box import print_flower_box_msg

    >>> msg_list = ['This is my first line test message',
    ...             'and my second line']
    >>> print_flower_box_msg(msg_list)
    <BLANKLINE>
    **************************************
    * This is my first line test message *
    * and my second line                 *
    **************************************

    """
    if isinstance(msgs, str):  # single message
        msgs = [msgs]  # convert to list

    max_msg_len: int = len(max(msgs, key=len)) + 4  # 4 for front/end asterisks

    # start with a new line so that our flower box is properly aligned
    print('\n' + '*' * max_msg_len, **kwargs)
    for msg in msgs:
        msg = '* ' + msg + ' ' * (max_msg_len - len(msg) - 4) + ' *'
        print(msg, **kwargs)
    print('*' * max_msg_len, **kwargs)
