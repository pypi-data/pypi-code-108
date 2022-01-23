from functools import partial
from itertools import chain, groupby
from typing import Callable, Dict, Generic, Iterable, Iterator, Tuple, TypeVar

from nonion.tools import compose, fst, lift, snd, value, zipmapl

V = TypeVar("V")
X = TypeVar("X")
Y = TypeVar("Y")
Z = TypeVar("Z")

AnyFunctionWithWrappedArguments = Callable[[Iterable[object], Dict[str, object]], Y]


class Function(Generic[X, Y]):
    pass


class Function(Generic[X, Y]):
    function: Callable[[X], Y]

    def __init__(self, function: Callable[[X], Y] = lambda x: x):
        self.function = function

    def __matmul__(self, function: Callable[[Z], X]) -> Function[Z, Y]:
        return self.compose(function)

    def compose(self, function: Callable[[Z], X]) -> Function[Z, Y]:
        return Function(compose(self.function, function))

    def __truediv__(self, function: Callable[[Y], Z]) -> Function[X, Z]:
        return self.then(function)

    def then(self, function: Callable[[Y], Z]) -> Function[X, Z]:
        return Function(compose(function, self.function))

    def __mul__(self, xs: Iterable[X]) -> Iterable[Y]:
        return self.foreach(xs)

    def fanout(self, function: Callable[[X], Z]) -> Function[X, Tuple[Y, Z]]:
        return Function(lambda x: (self.function(x), function(x)))

    def __xor__(self, function: Callable[[V], Z]) -> Function[Tuple[X, V], Tuple[Y, Z]]:
        return self.split(function)

    def split(self, function: Callable[[V], Z]) -> Function[Tuple[X, V], Tuple[Y, Z]]:
        return Function(lambda xv: (self.function(fst(xv)), function(snd(xv))))

    def __call__(self, x: X) -> Y:
        return self.function(x)

    def __or__(self, x: X) -> Y:
        return self.function(x)

    def foreach(self, xs: Iterable[X]) -> Iterable[Y]:
        return map(self.function, xs)

    def __and__(self, function: Callable[[X], Z]) -> Function[X, Tuple[Y, Z]]:
        return self.fanout(function)


def star(f: Callable[..., Y]) -> AnyFunctionWithWrappedArguments[Y]:
    def g(xs: Iterable[object], **kwargs: object) -> Y:
        return f(*xs, **kwargs)

    return g


def unstar(f: AnyFunctionWithWrappedArguments[Y]) -> Callable[..., Y]:
    def g(*args: object, **kwargs: object) -> object:
        return f(args, **kwargs)

    return g


class Pipeline(Generic[X]):
    pass


class Pipeline(Generic[X]):
    _xs: Iterable[X]

    def __init__(self, xs: Iterable[X] = ()):
        self._xs = xs

    def __truediv__(self, function: Callable[[X], Y]) -> Pipeline[Y]:
        return self.map(function)

    def map(self, function: Callable[[X], Y]) -> Pipeline[Y]:
        return Pipeline(function(x) for x in self._xs)

    def __mod__(self, predicate: Callable[[X], bool]) -> Pipeline[X]:
        return self.filter(predicate)

    def filter(self, predicate: Callable[[X], bool]) -> Pipeline[X]:
        return Pipeline(x for x in self._xs if predicate(x))

    def __mul__(self, function: Callable[[X], Iterable[Y]]) -> Pipeline[Y]:
        return self.flatmap(function)

    def flatmap(self, function: Callable[[X], Iterable[Y]]) -> Pipeline[Y]:
        return Pipeline(chain.from_iterable(function(x) for x in self._xs))

    def __floordiv__(
        self, function: Callable[[Iterator[X]], Iterable[Y]]
    ) -> Pipeline[Y]:
        return self.apply(function)

    def apply(self, function: Callable[[Iterator[X]], Iterable[Y]]) -> Pipeline[Y]:
        return Pipeline(function(iter(self._xs)))

    def __rshift__(self, function: Callable[[Iterator[X]], Y]) -> Y:
        return self.collect(function)

    def collect(self, function: Callable[[Iterator[X]], Y]) -> Y:
        return function(iter(self._xs))

    def __or__(self, consumer: Callable[[X], None]):
        return self.foreach(consumer)

    def foreach(self, consumer: Callable[[X], None]):
        for x in self._xs:
            consumer(x)

    def __iter__(self) -> Iterator[X]:
        return iter(self._xs)


def groupon(
    f: Callable[[X], Y]
) -> Callable[[Iterable[X]], Iterable[Tuple[Y, Iterable[X]]]]:
    def g(xs: Iterable[X]) -> Iterable[Tuple[Y, Iterable[X]]]:
        yxs = Pipeline(xs) // zipmapl(f) >> partial(sorted, key=fst)

        grouped = groupby(yxs, key=fst)

        return Pipeline(grouped) / value(lift(snd))

    return g
