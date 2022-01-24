from unittest import TestCase
from chibi_command.network import NMcli


class nmcli( TestCase ):
    def test_connections_should_return_a_list( self ):
        connections = NMcli.connections()
        self.assertTrue( connections )
        self.assertIsInstance( connections.result, list )
        self.assertTrue( connections.result )
        for r in connections.result:
            self.assertIsInstance( r, dict )

    def test_all_the_connections_should_have_detail( self ):
        connections = NMcli.connections()
        self.assertTrue( connections )
        for connection in connections.result:
            self.assertTrue( connection.detail )
            self.assertIsInstance( connection.detail, dict )

    def test_current_should_return_a_single_connection( self ):
        connection = NMcli.current()
        self.assertIsNotNone(
            connection, "no se encontro la conexion actual" )
        self.assertTrue( connection )
        self.assertIsInstance( connection, dict )

    def test_current_connection_should_have_detail( self ):
        connection = NMcli.current()
        self.assertIsNotNone(
            connection, "no se encontro la conexion actual" )
        detail = connection.detail
        self.assertTrue( detail )
        self.assertIsInstance( detail, dict )
