#!/usr/bin/python
"""\
@file   test_deco.py
@author Nat Goodspeed
@date   2020-10-29
@brief  Test deco.py functionality

Copyright (c) 2020, Nat Goodspeed
"""

from contextlib import contextmanager
from pyng.deco import within, DontCall
import unittest

module_context = None

# Code an explicit context manager class here to test @within(instance);
# contextlib.contextmanager only addresses functions returning context
# manager.
class ContextManager(object):
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        global module_context
        module_context = self.context
        return module_context

    def __exit__(self, type, value, traceback):
        global module_context
        module_context = None
        # don't swallow exceptions
        return False

# canonical instance
module_context_manager = ContextManager('module')

class BadCall(Exception):
    pass

class CallableContextManager(ContextManager):
    # example of a multi-purpose class whose instance can be either a context
    # manager or a callable
    def __call__(self):
        raise BadCall('should not have called CallableContextManager instance')

class TestWithin(unittest.TestCase):
    def setUp(self):
        self.context = None

    # class attribute context manager
    class_context_manager = ContextManager('class')

    def test_ContextManager(self):
        global module_context
        # first, ensure that ContextManager does what we think it does
        self.assertFalse(callable(module_context_manager))
        self.assertEqual(module_context, None)
        with ContextManager('test') as context:
            self.assertEqual(module_context, 'test')
            self.assertEqual(context, 'test')
        self.assertEqual(module_context, None)

    def test_CallableContextManager(self):
        self.assertTrue(callable(CallableContextManager('test')))

    @within(module_context_manager)
    def test_within_module_instance(self):
        self.assertEqual(module_context, 'module')

    @within(module_context_manager)
    def test_within_module_instance_context(self, _context=None):
        self.assertEqual(module_context, 'module')
        self.assertEqual(_context, 'module')

    @within(module_context_manager)
    def test_within_module_instance_kwds(self, **kwds):
        self.assertEqual(module_context, 'module')
        self.assertEqual(kwds['_context'], 'module')

    @within(class_context_manager)
    def test_within_class_instance(self):
        self.assertEqual(module_context, 'class')

    @within(class_context_manager)
    def test_within_class_instance_context(self, _context=None):
        self.assertEqual(module_context, 'class')
        self.assertEqual(_context, 'class')

    @within(class_context_manager)
    def test_within_class_instance_kwds(self, **kwds):
        self.assertEqual(module_context, 'class')
        self.assertEqual(kwds['_context'], 'class')

    @within(ContextManager, 'temp')
    def test_within_class(self):
        self.assertEqual(module_context, 'temp')

    @within(ContextManager, context='temp')
    def test_within_class_context(self, _context=None):
        self.assertEqual(module_context, 'temp')
        self.assertEqual(_context, 'temp')

    @within(ContextManager, 'temp')
    def test_within_class_kwds(self, **kwds):
        self.assertEqual(module_context, 'temp')
        self.assertEqual(kwds['_context'], 'temp')

    @within(CallableContextManager('whoops'))
    def callable_instance(self):
        raise AssertionError("shouldn't have reached callable_instance() body")

    def test_callable_instance(self):
        # The point of this test is that for callable_instance(), we passed
        # within() an *instance* of CallableContextManager rather than the
        # class. That would be fine except that CallableContextManager is
        # itself callable, but calling it in the 'with' statement in our
        # wrapper function is wrong: it's not going to return a context
        # manager, instead it's going to raise BadCall.
        with self.assertRaises(BadCall):
            self.callable_instance()

    @within(DontCall(CallableContextManager('uncalled')))
    def test_dontcall_instance(self):
        self.assertEqual(module_context, 'uncalled')
