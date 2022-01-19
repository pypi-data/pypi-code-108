from typing import Generic, TypeVar, Callable

A = TypeVar('A')
R = TypeVar('R')


class Predicate(Generic[A]):  # Predicate[A] = Callable[A,bool] - unsupported by Python at the moment
    """
    Predicate along with text description
    """

    # note that fn: Callable[..., bool]
    # means that fn takes an arbitrary number of args of any type
    #
    # type safety is preserved by type annotations on __call__() methods
    # (where fn is actually called)
    def __init__(self, expr: str, fn: Callable[..., bool]):
        self.expr = expr
        self.fn = fn

    def __call__(self, *args: A) -> bool:
        return self.fn(*args)

    def And(self, other: 'Predicate[A]') -> 'Predicate[A]':
        return Predicate(self.expr + " and " + other.expr, lambda a: self(a) and other(a))

    def Or(self, other: 'Predicate[A]') -> 'Predicate[A]':
        return Predicate(self.expr + " or " + other.expr, lambda a: self(a) or other(a))

    def Not(self) -> 'Predicate[A]':
        return Predicate("not " + self.expr, lambda a: not self(a))


class TreeNode(Generic[A, R]):  # in fact it's callable(Callable[[A], R]):
    """Root class representing an arbitrary tree node - either branching or result"""

    def __call__(self, *args: A) -> R:
        pass


class DecisionTreeNode(TreeNode[A, R]):
    """Class represents a branching decision tree node"""
    result = ""

    def __init__(self, name, predicate: Predicate[A], on_true: TreeNode[A, R], on_false: TreeNode[A, R]):
        self.name = name
        self.predicate = predicate
        self.on_true = on_true
        self.on_false = on_false

    def __call__(self, *args: A) -> R:
        flag = self.predicate(*args)
        self.result = self.predicate.expr + " = " + str(flag)
        if flag:
            return self.on_true(*args)
        else:
            return self.on_false(*args)


class ResultTreeNode(TreeNode[A, R]):
    """Only returns the result """

    def __init__(self, fn: Callable[..., R]):
        self.fn = fn

    def __call__(self, *args: A) -> R:
        return self.fn(*args)
