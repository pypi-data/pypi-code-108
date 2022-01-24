import unittest

from graphdb.schema import Node


class TestNode(unittest.TestCase):

    def setUp(self) -> None:
        self.node_without_prop = {"label": "Person", "primary_key": "name"}
        self.node_with_prop = {"label": "Person", "primary_key": "name", "properties": {
            "name": "Dann",
            "job": "developer"
        }}
        self.node_without_label = {"primary_key": "name", "properties": {
            "name": "Ann",
            "job": "system engineer"
        }}

    def test_create_node_without_prop(self):
        """Test create new node with property
        :return: none
        """
        node = Node(**self.node_without_prop)
        self.assertEqual(node.label, self.node_without_prop["label"])
        self.assertEqual(node.primary_key, self.node_without_prop["primary_key"])

    def test_create_node_with_prop(self):
        """Test create new node with property
        :return: none
        """
        node = Node(**self.node_with_prop)
        self.assertEqual(node.label, self.node_with_prop["label"])
        self.assertEqual(node.primary_key, self.node_with_prop["primary_key"])
        self.assertEqual(node.properties, self.node_with_prop["properties"])

    def test_create_node_without_label(self):
        """This will throw an error when try to build node without label
        :return: none
        """
        with self.assertRaises(Exception):
            Node(**self.node_without_label)
