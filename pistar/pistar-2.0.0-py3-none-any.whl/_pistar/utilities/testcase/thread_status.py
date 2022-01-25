"""
description: this module provides class Status.
"""


class And:
    """
    description: this is and operator of status.
    """

    left = None
    right = None

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "({left} and {right})".format(left=str(self.left.value), right=str(self.right.value))

    def __call__(self):
        left = self.left() if callable(self.left) else self.left.value
        right = self.right() if callable(self.right) else self.right.value
        return left & right


class Or:
    """
    description: this is or operator of status.
    """

    left = None
    right = None

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "({left} or {right})".format(left=str(self.left.value), right=str(self.right.value))

    def __call__(self):
        left = self.left() if callable(self.left) else self.left.value
        right = self.right() if callable(self.right) else self.right.value
        return left | right


class Status:
    """
    description: this class provides delay calculation of status.
    """

    value = None

    def __init__(self, value):
        self.value = value

    def __and__(self, other):
        return Status(And(self, other))

    def __or__(self, other):
        return Status(Or(self, other))

    def __repr__(self):
        return str(self.value)

    def __call__(self):
        if not isinstance(self.value, (Or, And)):
            return self.value
        return self.value()
