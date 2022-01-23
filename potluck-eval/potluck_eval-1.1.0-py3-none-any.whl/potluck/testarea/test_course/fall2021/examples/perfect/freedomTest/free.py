"""
Freedom test task solution.

free.py

Peter Mawhorter 2021-7-23
"""


def whatever(a, b):
    """
    We don't care what you return from this function, as long as you
    return different values when the arguments are both True, both
    False, or when one is True and the other is False. You must return
    the same value when one is True and the other is False regardless of
    which argument is True and which is False.
    """
    if a and b:
        return 1
    elif a:
        return 2
    elif b:
        return 2
    else:
        return 3


# Expectations

import optimism as opt

m = opt.testFunction(whatever)
m.case(True, True).checkResult(1)
m.case(True, False).checkResult(2)
m.case(False, True).checkResult(2)
m.case(False, False).checkResult(3)
