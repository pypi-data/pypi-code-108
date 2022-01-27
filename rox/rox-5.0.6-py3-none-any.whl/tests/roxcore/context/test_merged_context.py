import unittest

from rox.core.context.merged_context import MergedContext


class MergedContextTests(unittest.TestCase):
    def test_with_null_local_context(self):
        global_context = {'a': 1}
        merged_context = MergedContext(global_context, None)

        self.assertEqual(1, merged_context['a'])
        self.assertIsNone(merged_context['b'])

    def test_with_null_global_context(self):
        local_context = {'a': 1}
        merged_context = MergedContext(None, local_context)

        self.assertEqual(1, merged_context['a'])
        self.assertIsNone(merged_context['b'])

    def test_with_local_and_global_context(self):
        global_context = {'a': 1, 'b': 2}
        local_context = {'a': 3, 'c': 4}
        merged_context = MergedContext(global_context, local_context)

        self.assertEqual(3, merged_context['a'])
        self.assertEqual(2, merged_context['b'])
        self.assertEqual(4, merged_context['c'])
        self.assertIsNone(merged_context['d'])
