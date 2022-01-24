from __future__ import annotations
from myqueue.workflow import run


def f(name='hi'):
    """Function that can fail with MEMORY error."""
    if name == 'oom':
        raise MemoryError


def workflow():
    """Long dependency chain."""
    d1 = run(function=f, name='1', args=['oom'])
    d2 = run(function=f, name='2', deps=[d1])
    d3 = run(function=f, name='3', deps=[d2])
    run(function=f, name='4', deps=[d3])
