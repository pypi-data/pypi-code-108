import unittest
import unittest.mock

from guide_bot.requirements.requirement_parameters import Parameters
from guide_bot.requirements.requirement_parameters import InputConfigurationIterator


def setup_simple():
    """
    Creates simple Parameters object with allowed types, but no scan
    """
    pars = Parameters()
    pars.add("int_par", 4)
    pars.add("str_par", "test")
    pars.add("float_par", 9)
    pars.add("none_par", None)
    return pars


def setup_simple_scan():
    """
    Adds a scanned parameter to the simple Parameters object
    """
    pars = setup_simple()
    pars.add("scan_par", [1.1, 9, "answer"])
    return pars

def setup_simple_scan_with_bool():
    """
    Adds a scanned parameter to the simple Parameters object
    """
    pars = setup_simple()
    pars.add("scan_par", [1.1, 9, "answer", True, False])
    return pars


def setup_scan():
    """
    Adds a second scanned parameter to the scanned Parameters object
    """
    pars = setup_simple_scan()
    pars.add("new_scan_par", [1, 2, 3])
    return pars


class TestRequirementParameters(unittest.TestCase):
    def test_basic_Parameters(self):
        """
        Testing a Parameters object can be made
        """

        pars = Parameters()

        self.assertEqual(pars.get_n_scanned_parameters(), 0)
        self.assertEqual(pars.get_scan_shape(), [])

    def test_simple_Parameters(self):
        """
        Testing a simple Parameters object
        """

        pars = setup_simple()

        self.assertEqual(pars.get_n_scanned_parameters(), 0)
        self.assertEqual(pars.get_scan_shape(), [])

        self.assertEqual(pars["int_par"], 4)
        self.assertEqual(pars["str_par"], "test")
        self.assertEqual(pars["float_par"], 9)
        self.assertEqual(pars["none_par"], None)

    def test_simple_scan_Parameters(self):
        """
        Test Parameters with a scanned parameter, using its state
        """
        pars = setup_simple_scan()

        self.assertEqual(pars.get_n_scanned_parameters(), 1)
        self.assertEqual(pars.get_scan_shape(), [3])

        self.assertEqual(pars["int_par"], 4)
        self.assertEqual(pars["str_par"], "test")
        self.assertEqual(pars["float_par"], 9)
        self.assertEqual(pars["none_par"], None)

        pars.set_state([0])
        self.assertEqual(pars["scan_par"], 1.1)
        pars.set_state([1])
        self.assertEqual(pars["scan_par"], 9)
        pars.set_state([2])
        self.assertEqual(pars["scan_par"], "answer")

    def test_simple_scan_with_bool_Parameters(self):
        """
        Test Parameters with a scanned parameter, using its state
        """
        pars = setup_simple_scan_with_bool()

        self.assertEqual(pars.get_n_scanned_parameters(), 1)
        self.assertEqual(pars.get_scan_shape(), [5])

        self.assertEqual(pars["int_par"], 4)
        self.assertEqual(pars["str_par"], "test")
        self.assertEqual(pars["float_par"], 9)
        self.assertEqual(pars["none_par"], None)

        pars.set_state([0])
        self.assertEqual(pars["scan_par"], 1.1)
        pars.set_state([1])
        self.assertEqual(pars["scan_par"], 9)
        pars.set_state([2])
        self.assertEqual(pars["scan_par"], "answer")
        pars.set_state([3])
        self.assertEqual(pars["scan_par"], True)
        pars.set_state([4])
        self.assertEqual(pars["scan_par"], False)

    def test_simple_scan_Parameters(self):
        """
        Test Parameters object with two scanned parameters
        """

        pars = setup_scan()

        self.assertEqual(pars.get_n_scanned_parameters(), 2)
        self.assertEqual(pars.get_scan_shape(), [3, 3])

        self.assertEqual(pars["int_par"], 4)
        self.assertEqual(pars["str_par"], "test")
        self.assertEqual(pars["float_par"], 9)
        self.assertEqual(pars["none_par"], None)

        pars.set_state([0,0])
        self.assertEqual(pars["scan_par"], 1.1)
        self.assertEqual(pars["new_scan_par"], 1)
        pars.set_state([1,0])
        self.assertEqual(pars["scan_par"], 9)
        self.assertEqual(pars["new_scan_par"], 1)
        pars.set_state([2,0])
        self.assertEqual(pars["scan_par"], "answer")
        self.assertEqual(pars["new_scan_par"], 1)
        pars.set_state([0, 1])
        self.assertEqual(pars["scan_par"], 1.1)
        self.assertEqual(pars["new_scan_par"], 2)
        pars.set_state([1, 1])
        self.assertEqual(pars["scan_par"], 9)
        self.assertEqual(pars["new_scan_par"], 2)
        pars.set_state([2, 1])
        self.assertEqual(pars["scan_par"], "answer")
        self.assertEqual(pars["new_scan_par"], 2)
        pars.set_state([0, 2])
        self.assertEqual(pars["scan_par"], 1.1)
        self.assertEqual(pars["new_scan_par"], 3)
        pars.set_state([1, 2])
        self.assertEqual(pars["scan_par"], 9)
        self.assertEqual(pars["new_scan_par"], 3)
        pars.set_state([2, 2])
        self.assertEqual(pars["scan_par"], "answer")
        self.assertEqual(pars["new_scan_par"], 3)

    def test_scan_lock_Parameters(self):
        """
        Test that two scanned parameters can be locked
        """

        pars = setup_scan()

        pars.lock_parameters("scan_par", "new_scan_par")

        self.assertEqual(pars.get_n_scanned_parameters(), 1)
        self.assertEqual(pars.get_scan_shape(), [3])

        self.assertEqual(pars["int_par"], 4)
        self.assertEqual(pars["str_par"], "test")
        self.assertEqual(pars["float_par"], 9)
        self.assertEqual(pars["none_par"], None)

        pars.set_state([0])
        self.assertEqual(pars["scan_par"], 1.1)
        self.assertEqual(pars["new_scan_par"], 1)
        pars.set_state([1])
        self.assertEqual(pars["scan_par"], 9)
        self.assertEqual(pars["new_scan_par"], 2)
        pars.set_state([2])
        self.assertEqual(pars["scan_par"], "answer")
        self.assertEqual(pars["new_scan_par"], 3)

    def test_scan_lock_reversed_Parameters(self):
        """
        Reversing the order of locked parameters should not matter
        """

        pars = setup_scan()

        pars.lock_parameters("new_scan_par", "scan_par")

        self.assertEqual(pars.get_n_scanned_parameters(), 1)
        self.assertEqual(pars.get_scan_shape(), [3])

        self.assertEqual(pars["int_par"], 4)
        self.assertEqual(pars["str_par"], "test")
        self.assertEqual(pars["float_par"], 9)
        self.assertEqual(pars["none_par"], None)

        pars.set_state([0])
        self.assertEqual(pars["scan_par"], 1.1)
        self.assertEqual(pars["new_scan_par"], 1)
        pars.set_state([1])
        self.assertEqual(pars["scan_par"], 9)
        self.assertEqual(pars["new_scan_par"], 2)
        pars.set_state([2])
        self.assertEqual(pars["scan_par"], "answer")
        self.assertEqual(pars["new_scan_par"], 3)

    def test_scan_prefaced_Parameters(self):
        """
        Tests the preface name function does not impact behavior
        """

        pars = setup_simple_scan()

        pars.preface_names("prefix_test_")

        self.assertTrue("prefix_test_int_par" in pars.parameters)
        self.assertEqual(pars.parameters["prefix_test_int_par"], 4)

        self.assertEqual(pars.get_n_scanned_parameters(), 1)
        self.assertEqual(pars.get_scan_shape(), [3])

        self.assertEqual(pars["int_par"], 4)
        self.assertEqual(pars["str_par"], "test")
        self.assertEqual(pars["float_par"], 9)
        self.assertEqual(pars["none_par"], None)

        pars.set_state([0])
        self.assertEqual(pars["scan_par"], 1.1)
        pars.set_state([1])
        self.assertEqual(pars["scan_par"], 9)
        pars.set_state([2])
        self.assertEqual(pars["scan_par"], "answer")

    def test_scan_lock_prefaced_Parameters(self):
        """
        Test that prefaced parameters can still be locked
        """
        pars = setup_scan()

        pars.preface_names("prefix_test_")
        pars.lock_parameters("new_scan_par", "scan_par")

        self.assertEqual(pars.get_n_scanned_parameters(), 1)
        self.assertEqual(pars.get_scan_shape(), [3])

        self.assertEqual(pars["int_par"], 4)
        self.assertEqual(pars["str_par"], "test")
        self.assertEqual(pars["float_par"], 9)
        self.assertEqual(pars["none_par"], None)

        pars.set_state([0])
        self.assertEqual(pars["scan_par"], 1.1)
        self.assertEqual(pars["new_scan_par"], 1)
        pars.set_state([1])
        self.assertEqual(pars["scan_par"], 9)
        self.assertEqual(pars["new_scan_par"], 2)
        pars.set_state([2])
        self.assertEqual(pars["scan_par"], "answer")
        self.assertEqual(pars["new_scan_par"], 3)

    def test_scan_lock_prefaced_after_Parameters(self):
        """
        Test that prefacing parameters after locking works
        """

        pars = setup_scan()

        pars.lock_parameters("new_scan_par", "scan_par")
        pars.preface_names("prefix_test_")

        self.assertEqual(pars.get_n_scanned_parameters(), 1)
        self.assertEqual(pars.get_scan_shape(), [3])

        self.assertEqual(pars["int_par"], 4)
        self.assertEqual(pars["str_par"], "test")
        self.assertEqual(pars["float_par"], 9)
        self.assertEqual(pars["none_par"], None)

        pars.set_state([0])
        self.assertEqual(pars["scan_par"], 1.1)
        self.assertEqual(pars["new_scan_par"], 1)
        pars.set_state([1])
        self.assertEqual(pars["scan_par"], 9)
        self.assertEqual(pars["new_scan_par"], 2)
        pars.set_state([2])
        self.assertEqual(pars["scan_par"], "answer")
        self.assertEqual(pars["new_scan_par"], 3)


class something_with_parameters:
    def __init__(self):
        self.parameters = Parameters()

def setup_something_with_parameters():
    A = something_with_parameters()
    A.parameters = setup_simple()
    return A

def setup_scan_something_with_parameters():
    A = something_with_parameters()
    A.parameters = setup_simple_scan() #pars.add("scan_par", [1.1, 9, "answer"])
    return A

def simple_InputConfigurationIterator():
    A = setup_something_with_parameters()
    B = setup_something_with_parameters()

    return A, B, InputConfigurationIterator(A, B)

def simple_scan_InputConfigurationIterator():
    A = setup_scan_something_with_parameters()
    B = setup_something_with_parameters()

    return A, B, InputConfigurationIterator(A, B)

def scan_InputConfigurationIterator():
    A = setup_scan_something_with_parameters()
    B = setup_scan_something_with_parameters()

    return A, B, InputConfigurationIterator(A, B)


class TestInputConfigurationIterator(unittest.TestCase):
    def test_basic_Iterator(self):
        """
        Test that an iterator can be made
        """

        A, B, iterator = simple_InputConfigurationIterator()
        iterator.reset_configuration()

        self.assertTrue(iterator.next_state())
        self.assertFalse(iterator.next_state())

    def test_basic_Iterator_scan_steps(self):
        """
        Test that an iterator can be made and has right number of steps
        """

        A, B, iterator = simple_scan_InputConfigurationIterator()
        iterator.reset_configuration()

        self.assertTrue(iterator.next_state())
        self.assertTrue(iterator.next_state())
        self.assertTrue(iterator.next_state())
        self.assertFalse(iterator.next_state())

    def test_basic_Iterator_scan(self):
        """
        Test that an iterator can be made and scans something
        """

        A, B, iterator = simple_scan_InputConfigurationIterator()
        iterator.reset_configuration()

        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], 1.1)
        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], 9)
        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], "answer")
        self.assertFalse(iterator.next_state())

    def test_Iterator_scan(self):
        """
        Test that an iterator can be made and scans two parameters
        """

        A, B, iterator = scan_InputConfigurationIterator()
        iterator.reset_configuration()

        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], 1.1)
        self.assertEqual(B.parameters["scan_par"], 1.1)
        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], 1.1)
        self.assertEqual(B.parameters["scan_par"], 9)
        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], 1.1)
        self.assertEqual(B.parameters["scan_par"], "answer")

        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], 9)
        self.assertEqual(B.parameters["scan_par"], 1.1)
        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], 9)
        self.assertEqual(B.parameters["scan_par"], 9)
        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], 9)
        self.assertEqual(B.parameters["scan_par"], "answer")

        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], "answer")
        self.assertEqual(B.parameters["scan_par"], 1.1)
        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], "answer")
        self.assertEqual(B.parameters["scan_par"], 9)
        self.assertTrue(iterator.next_state())
        self.assertEqual(A.parameters["scan_par"], "answer")
        self.assertEqual(B.parameters["scan_par"], "answer")
        self.assertFalse(iterator.next_state())

