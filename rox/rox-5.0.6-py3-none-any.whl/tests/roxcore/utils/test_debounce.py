import unittest
import time
from rox.core.utils.debounce import debounce

class DebounceTests(unittest.TestCase):
    @debounce(seconds = 1)
    def call_after_interval(self):
        self.counter += 1

    def test_will_debounce_call_after_invoke(self):
        self.counter = 0

        self.assertEqual(0, self.counter)
        self.call_after_interval()
        self.assertEqual(0, self.counter)
        time.sleep(0.5)
        self.assertEqual(0, self.counter)
        time.sleep(0.6)
        self.assertEqual(1, self.counter)

    def test_will_debounce_cancel_early_invoke(self):
        self.counter = 0

        self.assertEqual(0, self.counter)
        self.call_after_interval()
        self.assertEqual(0, self.counter)
        time.sleep(0.5)
        self.assertEqual(0, self.counter)
        self.call_after_interval()
        self.assertEqual(0, self.counter)
        time.sleep(0.6)
        self.assertEqual(1, self.counter)
        time.sleep(0.6)
        self.assertEqual(1, self.counter)

    def test_will_debounce_invoke_enough_time_after_invoke(self):
        self.counter = 0

        self.assertEqual(0, self.counter)
        self.call_after_interval()
        self.assertEqual(0, self.counter)
        time.sleep(1.1)
        self.assertEqual(1, self.counter)
        self.call_after_interval()
        self.assertEqual(1, self.counter)
        time.sleep(0.8)
        self.assertEqual(1, self.counter)
        time.sleep(0.3)
        self.assertEqual(2, self.counter)