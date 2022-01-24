from __future__ import annotations
from myqueue.workflow import run as run0, wrap, resources


def run(**kwargs):
    return run0(args=['hello', 'world'], **kwargs)


@resources(tmax='1m')
def workflow():
    """Hello world."""
    print(1)
    with run(shell='echo'):
        print(2)
        with run(module='myqueue.test.hello'):
            with resources(tmax='2m'):
                print(3)
                with run(function=print, name='p1'):
                    print(4)
                    with run(script=__file__, tmax='3m'):
                        print(5)
                        with run(script='hello.sh'):
                            print(6)
                            wrap(print)('hello', 'world')


if __name__ == '__main__':
    import sys
    print(*sys.argv[1:])
