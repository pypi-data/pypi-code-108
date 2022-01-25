from ..sc_test_case import SCTestCase
from ...opencell_models.opencell_types.description import Description


class OpenCellDescriptionTypeTests(SCTestCase):

    def test_description_truncate_the_strings_with_50_chars(self):
        long_str = "Foo" * 50

        description_str = Description(long_str).text

        self.assertEqual(description_str, long_str[:50])
        self.assertTrue(len(description_str) == 50)
