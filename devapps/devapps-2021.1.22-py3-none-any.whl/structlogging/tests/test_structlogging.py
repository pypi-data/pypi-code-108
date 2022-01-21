#!/usr/bin/python -tt
from __future__ import absolute_import, division, print_function

import unittest
from functools import partial

import structlog as sl

# import ax.rx

try:
    pass

    have_gevent = True
except:
    have_gevent = False


# great to not have to inspect log files for the result:
RL = sl.ReturnLogger
# logger factory:
fac = lambda L, *a, **kw: L(*a, **kw)


def cfg_insert_proc(_, __, ev, **cfg):
    ev.update(cfg)
    return ev


class TestStructlogging(unittest.TestCase):
    def setUp(self):
        """
        """
        self.p1 = partial(cfg_insert_proc, p1='p1')
        self.p2 = partial(cfg_insert_proc, p2='p2')
        self.p3 = lambda _, __, ev: str(ev)

    def tearDown(self):
        """
        """

    def test_basic1(self):
        l = sl.wrap_logger(RL(), processors=[self.p1, self.p2])
        res = l.info('foo')[1]
        self.assertIn('p1', res)
        self.assertIn('p2', res)
        self.assertEqual(res['event'], 'foo')
        l2 = l.bind(key1='val1')
        res = l.debug('foo2')
        self.assertNotIn('key1', res)
        res2 = l2.debug('foo2')
        self.assertNotIn('key1', res2)

    def test_configure(self):
        l = sl.get_logger(RL(), processors=[self.p1, self.p2, self.p3])
        res = l.info('p1')
        # pdb.set_trace()


if __name__ == '__main__':
    unittest.main()
