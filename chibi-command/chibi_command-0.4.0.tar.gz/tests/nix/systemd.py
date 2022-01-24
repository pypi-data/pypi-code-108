from unittest import TestCase
import copy

from chibi.atlas import Chibi_atlas
from chibi_command import Command
from chibi_command import Command_result
from chibi_command.nix import Systemctl
from chibi_command.nix.systemd import Journal_status, Journal_show


class Test_systemctl( TestCase ):
    def test_status( self ):
        result = Systemctl.status( "unkown" ).run()
        self.assertIsNotNone( result )
        self.assertFalse( result )

        result = Systemctl.status( "NetworkManager" ).run()
        self.assertIsNotNone( result )
        self.assertTrue( result )
        self.assertIsInstance( result, Journal_status )
        self.assertEqual(
            'NetworkManager.service', result.result.service )

    def test_status_has_the_show_properites( self ):
        result = Systemctl.status( "NetworkManager" ).run()
        self.assertIn( 'properties', result.result )
        self.assertIsInstance( result.result.properties, Chibi_atlas )
        self.assertTrue( result.result.properties )

    def test_show( self ):
        result = Systemctl.show( "NetworkManager" ).run()
        self.assertIsNotNone( result )
        self.assertTrue( result )
        self.assertIsInstance( result, Journal_show )
        self.assertIsInstance( result.result, Chibi_atlas )

    def test_list_units( self ):
        result = Systemctl.list_units().run()
        for unit in result.result:
            self.assertIn( 'active', unit )
            self.assertIn( 'description', unit )
            self.assertIn( 'load', unit )
            self.assertIn( 'sub', unit )
            self.assertIn( 'unit', unit )
