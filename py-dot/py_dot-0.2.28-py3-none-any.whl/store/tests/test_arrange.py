import unittest

from py_dot.store.arrange import ArrangeCalculator

valid_items = [
    {
        'arrange': 1000000000000000,
        'sibling_order_amount': 1000000000000000,
        'after': 2000000000000000,
        'child_order_amount': 1000000000000,
        'first_child': 1001000000000000,
        'last_child': 1999000000000000
    },
    {
        'arrange': 1001000000000000,
        'sibling_order_amount': 1000000000000,
        'after': 1002000000000000,
        'child_order_amount': 1000000000,
        'first_child': 1001001000000000,
        'last_child': 1001999000000000
    },
    {
        'arrange': 1001001000000000,
        'sibling_order_amount': 1000000000,
        'after': 1001002000000000,
        'child_order_amount': 1000000,
        'first_child': 1001001001000000,
        'last_child': 1001001999000000
    },
    {
        'arrange': 1001001001000000,
        'sibling_order_amount': 1000000,
        'after': 1001001002000000,
        'child_order_amount': 1000,
        'first_child': 1001001001001000,
        'last_child': 1001001001999000
    },
    {
        'arrange': 1001001001001000,
        'sibling_order_amount': 1000,
        'after': 1001001001002000,
        'child_order_amount': 1,
        'first_child': 1001001001001001,
        'last_child': 1001001001001999
    },
    {
        'arrange': 11000000000000000,
        'sibling_order_amount': 1000000000000000,
        'after': 12000000000000000,
        'child_order_amount': 1000000000000,
        'first_child': 11001000000000000,
        'last_child': 11999000000000000
    },
    {
        'arrange': 11001000000000000,
        'sibling_order_amount': 1000000000000,
        'after': 11002000000000000,
        'child_order_amount': 1000000000,
        'first_child': 11001001000000000,
        'last_child': 11001999000000000
    },
    {
        'arrange': 11001001000000000,
        'sibling_order_amount': 1000000000,
        'after': 11001002000000000,
        'child_order_amount': 1000000,
        'first_child': 11001001001000000,
        'last_child': 11001001999000000
    },
    {
        'arrange': 11001001001000000,
        'sibling_order_amount': 1000000,
        'after': 11001001002000000,
        'child_order_amount': 1000,
        'first_child': 11001001001001000,
        'last_child': 11001001001999000
    },
    {
        'arrange': 11001001001001000,
        'sibling_order_amount': 1000,
        'after': 11001001001002000,
        'child_order_amount': 1,
        'first_child': 11001001001001001,
        'last_child': 11001001001001999
    }
]


class TestArrange(unittest.TestCase):
    def test_arranges(self):
        calculator = ArrangeCalculator()

        for valid_item in valid_items:
            item = calculator.item(valid_item['arrange'])

            test_value = {
                'arrange': item.arrange,
                'sibling_order_amount': item.sibling_order_amount,
                'after': item.after,
                'child_order_amount': item.child_order_amount,
                'first_child': item.first_child,
                'last_child': item.last_child
            }

            print(test_value)

            self.assertDictEqual(
                valid_item,
                test_value
            )
