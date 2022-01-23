import operator as op
from collections import deque
from functools import partial, reduce
from itertools import chain, compress, count, islice, product, repeat
from typing import Callable, Deque, Iterable, Iterator, Tuple, TypeVar, Union

X = TypeVar("X")
Y = TypeVar("Y")
Z = TypeVar("Z")

Maybe = Union[Tuple[X], Tuple[()]]
Either = Tuple[Maybe[X], Maybe[Y]]


def compose(f: Callable[[Y], Z], g: Callable[[X], Y]) -> Callable[[X], Z]:
    return lambda x: f(g(x))


def curry(f: Callable[..., Y]) -> Callable[..., Y]:
    return lambda *args, **kwargs: partial(f, *args, **kwargs)


lift = curry(map)


def try_(
    f: Callable[..., Y], *args: object, **kwargs: object
) -> Callable[..., Maybe[Y]]:
    def g(*args_: object, **kwargs_: object) -> Maybe[Y]:
        try:
            return (f(*args, *args_, **{**kwargs, **kwargs_}),)
        except:
            return ()

    return g


def except_(
    f: Callable[..., Y], *args: object, **kwargs: object
) -> Callable[..., Either[Exception, Y]]:
    def g(*args_: object, **kwargs_: object) -> Either[Exception, Y]:
        try:
            y = f(*args, *args_, **{**kwargs, **kwargs_})
            return (), (y,)
        except Exception as e:
            return (e,), ()

    return g


next_: Callable[[Iterator[X]], Maybe[X]] = try_(next)


@curry
def finds(ps: Iterable[Callable[[X], bool]], xs: Iterable[X]) -> Iterable[Maybe[X]]:
    buffer = []

    for p in ps:
        x = find(p)(buffer)

        if not x:
            ys, xs = span(not_(p))(xs)
            x = next_(xs)
            buffer.extend(ys)

        yield x


@curry
def find(p: Callable[[X], bool], xs: Iterable[X]) -> Maybe[X]:
    xs = filter(p, xs)
    return next_(xs)


@curry
def findindex(p: Callable[[X], bool], xs: Iterable[X]) -> Maybe[int]:
    return next_(where(p)(xs))


def fst(xy: Tuple[X, Y]) -> X:
    return xy[0]


def snd(xy: Tuple[X, Y]) -> Y:
    return xy[1]


def slide(
    n: int = 2, step: int = 1, exact: bool = False
) -> Callable[[Iterable[X]], Iterable[Tuple[X, ...]]]:

    p = (lambda w: len(w) == n) if exact else (lambda w: len(w) > 0)

    def g(xs: Iterable[X]) -> Iterable[Tuple[X, ...]]:
        xs = iter(xs)

        window = islice(xs, n)
        window = tuple(window)

        while p(window):
            yield window

            window = chain(window[step:], islice(xs, step))
            window = tuple(window)

    return g


def take(n: int) -> Callable[[Iterable[X]], Iterable[X]]:
    return (lambda xs: islice(xs, n)) if n > 0 else (lambda _: ())


def drop(n: int) -> Callable[[Iterable[X]], Iterable[X]]:
    return (lambda xs: islice(xs, n, None)) if n > 0 else (lambda _: ())


def cache(f: Callable[..., Y], *args: object, **kwargs: object) -> Callable[..., Y]:
    f = partial(f, *args, **kwargs)

    def cached() -> Iterable[Y]:
        args_, kwargs_ = yield
        y = f(*args_, **kwargs_)

        while True:
            yield y

    cached = cached()
    next(cached)

    def g(*args_: object, **kwargs_: object) -> Y:
        return cached.send((args_, kwargs_))

    return g


def shift(f: Callable[..., Y], *args: object, **kwargs: object) -> Callable[..., Y]:
    return lambda *args_, **kwargs_: f(*args_, *args, **{**kwargs_, **kwargs})


def key(f: Callable[[X], Z]) -> Callable[[Tuple[X, Y]], Tuple[Z, Y]]:
    g: Callable[[Tuple[X, Y]], Z] = compose(f, fst)
    return lambda xy: (g(xy), snd(xy))


def value(f: Callable[[Y], Z]) -> Callable[[Tuple[X, Y]], Tuple[X, Z]]:
    g: Callable[[Tuple[X, Y]], Z] = compose(f, snd)
    return lambda xy: (fst(xy), g(xy))


def flip(f: Callable[[Y, X], Z]) -> Callable[[X, Y], Z]:
    return lambda x, y: f(y, x)


@curry
def foldl(f: Callable[[Y, X], Y], acc: Y, xs: Iterable[X]) -> Y:
    return reduce(f, xs, acc)


@curry
def foldr(f: Callable[[X, Y], Y], acc: Y, xs: Iterable[X]) -> Y:
    return foldl(flip(f), acc)(reversed(tuple(xs)))


@curry
def foldl1(f: Callable[[X, X], X], xs: Iterable[X]) -> X:
    return reduce(f, xs)


@curry
def foldr1(f: Callable[[X, X], X], xs: Iterable[X]) -> X:
    return foldl1(flip(f))(reversed(tuple(xs)))


@curry
def scanl(f: Callable[[Y, X], Y], acc: Y, xs: Iterable[X]) -> Iterable[Y]:
    yield acc

    for x in xs:
        acc = f(acc, x)
        yield acc


@curry
def scanr(f: Callable[[X, Y], Y], acc: Y, xs: Iterable[X]) -> Deque[Y]:
    def g(x: X, acc_: Deque[Y]) -> Deque[Y]:
        acc_.appendleft(f(x, acc_[0]))
        return acc_

    return foldr(g, deque([acc]))(xs)


@curry
def scanl1(f: Callable[[X, X], X], xs: Iterable[X]) -> Iterable[X]:
    xs = iter(xs)
    acc = next_(xs)

    if acc:
        return scanl(f, *acc)(xs)
    else:
        return ()


@curry
def scanr1(f: Callable[[X, X], X], xs: Iterable[X]) -> Deque[X]:
    xs = tuple(xs)

    if len(xs) > 0:
        return scanr(f, xs[-1])(xs[:-1])
    else:
        return deque()


def zipl(xs: Iterable[X]) -> Callable[[Iterable[Y]], Iterable[Tuple[X, Y]]]:
    return lambda ys: zip(xs, ys)


def zipr(ys: Iterable[Y]) -> Callable[[Iterable[X]], Iterable[Tuple[X, Y]]]:
    return lambda xs: zip(xs, ys)


def flattenl(xyz: Tuple[Tuple[X, Y], Z]) -> Tuple[X, Y, Z]:
    (*xy,), *z = xyz
    return (*xy, *z)


def flattenr(xyz: Tuple[X, Tuple[Y, Z]]) -> Tuple[X, Y, Z]:
    *x, (*yz,) = xyz
    return (*x, *yz)


def zipmapl(f: Callable[[X], Y]) -> Callable[[Iterable[X]], Iterable[Tuple[Y, X]]]:
    return lambda xs: map(lambda x: (f(x), x), xs)


def zipmapr(f: Callable[[X], Y]) -> Callable[[Iterable[X]], Iterable[Tuple[X, Y]]]:
    return lambda xs: map(lambda x: (x, f(x)), xs)


def as_match(xys: Iterable[Tuple[X, Y]]) -> Callable[[X], Maybe[Y]]:
    x_to_y = dict(xys)

    def lookup(x: X) -> Maybe[Y]:
        return (x_to_y[x],) if x in x_to_y else ()

    return lookup


def match_(*fs: Callable[..., Maybe[Y]]) -> Callable[..., Maybe[Y]]:
    def g(*args: object, **kwargs: object) -> Maybe[Y]:
        mys = map(lambda f: f(*args, **kwargs), fs)
        filtered_ys = filter(lambda y: y, mys)
        ys = map(fst, filtered_ys)

        return next_(ys)

    return g


def catch(*fs: Callable[..., Maybe[Y]], default: Callable[..., Y]) -> Callable[..., Y]:
    f = match_(*fs)

    def g(*args: object, **kwargs: object) -> Y:
        y, *_ = f(*args, **kwargs) or (default(*args, **kwargs),)
        return y

    return g


def stripby(compare: Callable[[X, X], bool]) -> Callable[[Iterable[X]], Iterable[X]]:
    return compose(lift(fst), groupby(compare))


def groupby(
    compare: Callable[[X, X], bool]
) -> Callable[[Iterable[X]], Iterable[Tuple[X, ...]]]:
    h: Callable[[X], Callable[[X], bool]] = curry(compare)

    def g(xs: Iterable[X]) -> Iterable[Tuple[X, ...]]:
        xs = iter(xs)
        mp = next_(xs)

        while mp:
            p, *_ = mp

            group, xs = span(h(p))(xs)
            yield mp + group

            mp = next_(xs)

    return g


@curry
def span(p: Callable[[X], bool], xs: Iterable[X]) -> Tuple[Tuple[X, ...], Iterable[X]]:
    xs = iter(xs)
    x = next_(xs)

    matched = []

    while x:
        if p(*x):
            matched.extend(x)
            x = next_(xs)
        else:
            break

    return tuple(matched), chain(x, xs)


strip: Callable[[Iterable[X]], Iterable[X]] = stripby(op.eq)
group: Callable[[Iterable[X]], Iterable[Tuple[X, ...]]] = groupby(op.eq)


def on(f: Callable[[Y, Y], Z], g: Callable[[X], Y]) -> Callable[[X, X], Z]:
    return lambda p, n: f(g(p), g(n))


@curry
def partition(
    p: Callable[[X], bool], xs: Iterable[X]
) -> Tuple[Tuple[X, ...], Tuple[X, ...]]:
    ts, fs = [], []

    for x in xs:
        if p(x):
            ts.append(x)
        else:
            fs.append(x)

    return tuple(ts), tuple(fs)


def powerset(xs: Tuple[X, ...]) -> Iterable[Iterable[X]]:
    ys = map(lambda _: range(2), range(len(xs)))
    return map(partial(compress, xs), product(*ys))


def between(low: float, high: float) -> Callable[[float], bool]:
    return lambda x: low <= x and x <= high


def in_(xs: Tuple[X, ...]) -> Callable[[X], bool]:
    return lambda x: x in xs


length: Callable[[Iterable[X]], int] = foldl(lambda acc, _: acc + 1, 0)


def not_(
    p: Callable[..., bool], *args: object, **kwargs: object
) -> Callable[..., bool]:
    return lambda *args_, **kwargs_: not p(*args, *args_, **{**kwargs, **kwargs_})


def zipflatl(
    f: Callable[[X], Maybe[Y]]
) -> Callable[[Iterable[X]], Iterable[Tuple[Y, X]]]:
    def g(xs: Iterable[X]) -> Iterable[Tuple[Y, X]]:
        ys = zipmapl(f)(xs)
        zs = filter(fst, ys)

        return map(key(fst), zs)

    return g


def zipflatr(
    f: Callable[[X], Maybe[Y]]
) -> Callable[[Iterable[X]], Iterable[Tuple[X, Y]]]:
    def g(xs: Iterable[X]) -> Iterable[Tuple[X, Y]]:
        ys = zipmapr(f)(xs)
        zs = filter(snd, ys)

        return map(value(fst), zs)

    return g


@curry
def as_catch(default: Callable[[X], Y], xys: Iterable[Tuple[X, Y]]) -> Callable[[X], Y]:
    return catch(as_match(xys), default=default)


@curry
def as_either(y: Callable[[], Y], x: Maybe[X]) -> Either[Y, X]:
    if x:
        return (), x
    else:
        return (y(),), ()


def peek(f: Callable[..., None], *args: object, **kwargs: object) -> Callable[..., X]:
    def g(x: X, *args_: object, **kwargs_: object) -> object:
        f(*args, x, *args_, **{**kwargs, **kwargs_})
        return x

    return g


@curry
def splitat(i: int, xs: Iterable[X]) -> Tuple[Tuple[X, ...], Iterable[X]]:
    xs = iter(xs)
    return tuple(islice(xs, i)), xs


def reverse(xs: Iterable[X]) -> Deque[X]:
    def g(acc: Deque[X], x: X) -> Deque[X]:
        acc.appendleft(x)
        return acc

    return foldl(g, deque())(xs)


@curry
def replicate(n: int, x: X) -> Iterable[X]:
    return take(n)(repeat(x))


@curry
def search(p: Callable[[X], bool], ys: Iterable[Y], xs: Iterable[X]) -> Iterable[Y]:
    filtered = filter(compose(p, snd), zip(ys, xs))
    return map(fst, filtered)


@curry
def where(p: Callable[[X], bool], xs: Iterable[X]) -> Iterable[int]:
    return search(p, count())(xs)


def fail(
    m: Callable[[Exception], Y], *args: object, **kwargs: object
) -> Callable[[Callable[..., Y]], Callable[..., Y]]:
    def g(f: Callable[..., Y], *args_: object, **kwargs_: object) -> Callable[..., Y]:
        def h(*args__: object, **kwargs__: object) -> Y:
            try:
                return f(*args, *args_, *args__, **{**kwargs, **kwargs_, **kwargs__})
            except Exception as e:
                return m(e)

        return h

    return g


def pickby(
    f: Callable[[X], Y],
    agg: Callable[[Tuple[Y, ...]], Y],
    compare: Callable[[Y, Y], bool] = op.eq,
) -> Callable[[Iterable[X]], Iterable[X]]:
    @fail(lambda _: ())
    def g(xs: Iterable[X]) -> Iterable[X]:
        xs = tuple(xs)
        ys = tuple(map(f, xs))
        y = agg(ys)

        p = compose(lambda z: compare(y, z), snd)
        return map(fst, filter(p, zip(xs, ys)))

    return g


def pick(
    agg: Callable[[Tuple[X, ...]], X], compare: Callable[[X, X], bool] = op.eq
) -> Callable[[Iterable[X]], Iterable[X]]:

    return pickby(lambda x: x, agg, compare)


def merge(
    xs: Iterable[X], ys: Iterable[X], key: Callable[[X], Y] = lambda x: x
) -> Iterable[X]:

    zipkey = compose(tuple, zipmapr(key))

    xs = iter(xs)
    ys = iter(ys)

    mx = next_(xs)
    my = next_(ys)

    if mx and my:
        mx, my = zipkey(mx), zipkey(my)

        while mx and my:
            ((x, cx), *_), ((y, cy), *_) = mx, my

            if cx <= cy:
                yield x
                mx = zipkey(next_(xs))
            else:
                yield y
                my = zipkey(next_(ys))

        mx, my = map(fst, mx), map(fst, my)

    yield from chain(mx, xs)
    yield from chain(my, ys)


def padl(n: int, x: X, exact: bool = False) -> Callable[[Iterable[X]], Iterable[X]]:
    if exact:
        g = lambda xs: chain(replicate(n)(x), xs)
    else:

        def g(xs: Iterable[X]) -> Iterable[X]:
            ys = tuple(xs)
            return chain(replicate(n - len(ys))(x), ys)

    return g


def padr(n: int, x: X, exact: bool = False) -> Callable[[Iterable[X]], Iterable[X]]:
    if exact:
        g = lambda xs: chain(xs, replicate(n)(x))
    else:

        def g(xs: Iterable[X]) -> Iterable[X]:
            ys = tuple(xs)
            return chain(ys, replicate(n - len(ys))(x))

    return g


def zipif(
    p: Callable[[X, Y], bool], f: Callable[[X, Y], Z], g: Callable[[X], Z]
) -> Callable[[Iterable[Y]], Callable[[Iterable[X]], Iterable[Z]]]:
    def h(xs: Iterable[X], ys: Iterable[Y]) -> Iterable[Z]:
        xs = iter(xs)
        ys = iter(ys)

        my = next_(ys)

        while my:
            mx = next_(xs)

            while True:
                if not mx:
                    return ()

                if p(*mx, *my):
                    yield f(*mx, *my)
                    break
                else:
                    yield g(*mx)
                    mx = next_(xs)

            my = next_(ys)

        yield from map(g, xs)

    return lambda ys: lambda xs: h(xs, ys)


def both(f: Callable[[X], Y]) -> Callable[[Tuple[X, X]], Tuple[Y, Y]]:
    return lambda xy: (f(fst(xy)), f(snd(xy)))
