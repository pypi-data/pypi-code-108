from chibi.nix import get_passwd
from unittest import TestCase
import copy

from chibi.atlas import Chibi_atlas
from chibi_command import Command
from chibi_command import Command_result
from chibi_command.nix import User


class Test_user( TestCase ):
    def test_exists( self ):
        self.assertTrue( User.name( 'root' ).exists )
        self.assertFalse( User.name( 'toor' ).exists )

    def test_create_should_return_a_command( self ):
        result = User.name( 'root' ).create
        self.assertIsInstance( result, Command )
