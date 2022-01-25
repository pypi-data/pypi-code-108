import unittest
from unittest.mock import Mock

from cloudshell.email.email_helpers import get_resource_attribute_value, build_sandbox_url


class TestHelpers(unittest.TestCase):

    def test_get_resource_attribute_value_with_namespace(self):
        # arrange
        resource = Mock(ResourceModelName="MyTestModel")
        resource.ResourceAttributes = [self._build_attribute("att1", "val1"),
                                       self._build_attribute(f"{resource.ResourceModelName}.att2", "val2")]

        # act
        result = get_resource_attribute_value(resource, "att2")

        # assert
        self.assertTrue("val2", result)

    def test_get_resource_attribute_value_without_namespace(self):
        # arrange
        resource = Mock()
        resource.ResourceAttributes = [self._build_attribute("att1", "val1"),
                                       self._build_attribute(f"att2", "val2")]

        # act
        result = get_resource_attribute_value(resource, "att2")

        # assert
        self.assertTrue("val2", result)

    def test_get_sandbox_url(self):
        # arrange
        sandbox_id = Mock()
        portal_base_url = "http://sandbox.com"

        # act
        sandbox_url = build_sandbox_url(portal_base_url, sandbox_id)

        # assert
        self.assertEqual(f"{portal_base_url}/RM/Diagram/Index/{sandbox_id}", sandbox_url)

    # region test helpers

    def _build_attribute(self, name: str, value: str) -> Mock:
        return Mock(Name=name, Value=value)

    # endregion
