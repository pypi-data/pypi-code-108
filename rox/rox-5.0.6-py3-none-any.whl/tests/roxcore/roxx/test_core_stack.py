import unittest

from rox.core.roxx.core_stack import CoreStack


class CoreStackTests(unittest.TestCase):
    def test_will_push_into_stack_string(self):
        test_string = 'stringTest'
        stack = CoreStack()
        stack.push(test_string)
        popped_item = stack.pop()
        self.assertEqual(test_string, popped_item)

    def test_will_push_into_stack_integer(self):
        test_int = 5
        stack = CoreStack()
        stack.push(test_int)
        popped_item = stack.pop()
        self.assertEqual(test_int, popped_item)

    def test_will_push_into_stack_integer_and_string(self):
        test_int = 5
        test_string = 'stringTest'
        stack = CoreStack()
        stack.push(test_int)
        stack.push(test_string)
        popped_item_first = stack.pop()
        popped_item_second = stack.pop()
        self.assertEqual(test_string, popped_item_first)
        self.assertEqual(test_int, popped_item_second)

    def test_will_peek_from_stack(self):
        test_int = 5
        test_string = 'stringTest'
        stack = CoreStack()
        stack.push(test_int)
        stack.push(test_string)
        peeked_item = stack.peek()
        popped_item = stack.pop()
        self.assertEqual(peeked_item, popped_item)
        self.assertEqual(test_string, popped_item)
