from __future__ import annotations
from myqueue.workflow import run, wrap, resources


def f(x: int) -> int:
    print(x)
    return x + 1


def work():
    A = []
    for x in range(3):
        y = f(x)
        f(y + 1)
        A.append(y)

    b = max(*A)

    if b > 2:
        print(b)

    return b


@resources(tmax='1h')
def workflow():
    A = []
    for x in range(3):
        y = wrap(f, name=f'fa-{x}')(x)
        run(function=f, name=f'fb-{x}', args=[y + 1])
        A.append(y)

    b = wrap(max)(*A)

    if b > 2:
        with resources(tmax='1s'):
            wrap(print)(b)

    return b


if __name__ == '__main__':
    workflow()
