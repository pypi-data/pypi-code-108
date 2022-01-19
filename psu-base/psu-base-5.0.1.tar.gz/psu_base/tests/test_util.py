from django.test import TestCase
from psu_base.services import utility_service


class UtilTestCase(TestCase):
    def setUp(self):
        pass

    def test_fake_session(self):
        """
        Since the session does not exist while unit testing, a dict is used in its place.
        This tests that the dict is functioning as expected
        """
        fake_session = utility_service.get_session()
        self.assertTrue(type(fake_session) is dict, "Session should be a dict")

        test_var_1 = "unit_test_value"
        test_val_1 = "This is a unit test..."
        utility_service.set_session_var(test_var_1, test_val_1)
        self.assertTrue(
            utility_service.get_session_var(test_var_1) == test_val_1,
            "Session var not set or retrieved",
        )

        test_var_2 = "unit_test_temp_value"
        test_val_2 = "This is another unit test..."
        utility_service.set_page_scope(test_var_2, test_val_2)
        self.assertTrue(
            utility_service.get_page_scope(test_var_2) == test_val_2,
            "Page scope var not set or retrieved",
        )
        utility_service.clear_page_scope()
        self.assertTrue(
            utility_service.get_page_scope(test_var_2) is None, "Page scope not cleared"
        )
        self.assertTrue(
            utility_service.get_session_var(test_var_1) == test_val_1,
            "Regular session mistakenly cleared",
        )

    def test_cache_keys(self):
        key = utility_service.test_cache_key()
        self.assertTrue(type(key) is str)
        self.assertTrue("test_cache_keys" in key)

    def test_store_recall_string(self):
        value = "fdfsdfd78fsd"
        utility_service.test_store_recall(value)
        self.assertTrue(utility_service.test_store_recall() == value)

    def test_store_recall_dict(self):
        value = {"one": "test", "two": 4, "three": [1, 2, 3, 4]}
        utility_service.test_store_recall(value)
        response = utility_service.test_store_recall()
        self.assertTrue(type(response) is dict)
        self.assertTrue(len(response) == 3)
        self.assertTrue(len(response["three"]) == 4)

        # Changing the original (mutable) response will affect the cached value as well
        value["four"] = "testing"
        self.assertTrue(len(response) == 4)
        self.assertTrue(response["four"] == "testing")
        self.assertTrue(response == value)

    def test_csv_conversion(self):
        self.assertTrue(
            utility_service.csv_to_list("1,2, 3 , 4") == ["1", "2", "3", "4"]
        )
        self.assertTrue(
            utility_service.csv_to_list("[1,2, 3 , 4]") == ["1", "2", "3", "4"]
        )
        self.assertTrue(
            utility_service.csv_to_list("1,2, 3 , 4", convert_int=True) == [1, 2, 3, 4]
        )
        self.assertTrue(
            utility_service.csv_to_list(["1", "2", "3", "4"]) == ["1", "2", "3", "4"]
        )
        self.assertTrue(
            utility_service.csv_to_list(["1", "2", "3", "4"], convert_int=True)
            == [1, 2, 3, 4]
        )
        self.assertTrue(utility_service.csv_to_list([1, 2, 3, 4]) == [1, 2, 3, 4])

    def test_to_choices(self):
        self.assertEqual(
            utility_service.to_choices({"Choice_id": "Choice_value"}),
            [("Choice_id", "Choice_value")],
        )
        self.assertEqual(
            utility_service.to_choices([{"id": "Choice_id", "value": "Choice_value"}]),
            [("Choice_id", "Choice_value")],
        )
        self.assertEqual(
            utility_service.to_choices([("Choice_id", "Choice_value")]),
            [("Choice_id", "Choice_value")],
        )
