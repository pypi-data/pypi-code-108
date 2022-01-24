import unittest

from graphdb import prepare_identifier, \
    make_identifier, parse_connection_uri


class TestUtil(unittest.TestCase):

    def setUp(self) -> None:
        self.example_identifier = {"name": "Ann", "age": 26}

    def test_prepare_identifier(self):
        """Test prepare identifier, this means we will create place holder for
        interaction with neo4j database
        :return: none
        """
        # test if all identifier is good
        identifier = prepare_identifier(self.example_identifier.keys())
        self.assertEqual(identifier, "{name: $name, age: $age}")

        # test if identifier is empty
        none_identifier = prepare_identifier({}.keys())
        self.assertEqual(none_identifier, "{}")

    def test_make_identifier(self):
        """Test to make identifier, this means we will create non place holder value, but need to remove
        quotes in json data see this test case
        :return: none
        """
        # test when identifier is not empty
        make_identifier_object = make_identifier(self.example_identifier)
        self.assertEqual(make_identifier_object, """{name: "Ann", age: "26"}""")

        # test when identifier is empty
        make_identifier_object = make_identifier({})
        self.assertEqual(make_identifier_object, """{}""")

    def test_parse_connection_uri_with_full_uri(self):
        """Test parse connection uri with full connection uri,
        this mean username and password is store in connection uri it self
        :return: none
        """
        conn_uri = "redis://username:secret@localhost:6379/0"
        new_con_uri, username, password = parse_connection_uri(conn_uri)
        self.assertEqual(new_con_uri, "redis://localhost:6379/0")
        self.assertEqual(username, "username")
        self.assertEqual(password, "secret")

    def test_parse_connection_uri_with_only_username(self):
        """Test parse connection uri with only username only
        :return: none
        """
        conn_uri = "redis://username:@localhost:6379/0"
        new_con_uri, username, password = parse_connection_uri(conn_uri)
        self.assertEqual(new_con_uri, "redis://localhost:6379/0")
        self.assertEqual(username, "username")
        self.assertEqual(password, "")

    def test_parse_connection_uri_with_only_password(self):
        """Test parse connection uri with only password only
        :return: none
        """
        conn_uri = "redis://:password@localhost:6379/0"
        new_con_uri, username, password = parse_connection_uri(conn_uri)
        self.assertEqual(new_con_uri, "redis://localhost:6379/0")
        self.assertEqual(username, "")
        self.assertEqual(password, "password")

    def test_parse_connection_uri_with_no_cred(self):
        """Test parse connection uri with no credential provided
        :return: none
        """
        conn_uri = "redis://localhost:6379/0"
        new_con_uri, username, password = parse_connection_uri(conn_uri)
        self.assertEqual(new_con_uri, "redis://localhost:6379/0")
        self.assertIsNone(username)
        self.assertIsNone(password)
