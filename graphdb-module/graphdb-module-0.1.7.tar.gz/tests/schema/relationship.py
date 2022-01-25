import unittest

from graphdb.schema import Relationship


class TestRelationship(unittest.TestCase):

    def setUp(self) -> None:
        self.rel = {"relationship_name": "FRIEND"}

    def test_create_relationship(self):
        """Test create new relationship
        :return: none
        """
        rel = Relationship(**self.rel)
        self.assertEqual(rel.relationship_name, self.rel["relationship_name"])

    def test_create_relationship_with_error(self):
        """Test to create relationship object without name,
        this will throw an error
        :return: none
        """
        with self.assertRaises(Exception):
            Relationship(**{})
