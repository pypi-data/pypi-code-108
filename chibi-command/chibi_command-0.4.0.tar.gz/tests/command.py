import re
import copy
from unittest import TestCase
from unittest.mock import patch

from chibi_command import Command, Command_json_result
from chibi_command.nix.systemd_run import System_run
from chibi_command.nix import Systemctl


class Test_echo( TestCase ):

    def test_can_build_a_new_command( self ):
        result = Command()
        self.assertEqual( "", result.preview(), )
        result = Command( "echo", "hello my world!" )
        self.assertEqual( "echo hello my world!", result.preview(), )
        result = Command()
        self.assertEqual( "", result.preview(), )

    def test_eq( self ):
        command_1 = Command( "echo" )
        command_2 = Command( "cowsay" )
        command_3 = Command( "echo" )
        self.assertNotEqual( command_1, command_2 )
        self.assertEqual( command_1, command_3 )

    def test_eq_with_str( self ):
        command_1 = Command( "echo" )
        self.assertNotEqual( command_1, 'cowsay' )
        self.assertEqual( command_1, 'echo' )

    def test_can_copy_the_command( self ):
        command = Command()
        new_command = copy.copy( command )
        self.assertEqual( command, new_command )

        command = Command( "echo" )
        new_command = copy.copy( command )
        self.assertEqual( command, new_command )

    def test_add_new_args( self ):
        command = Command( 'echo' )
        command.add_args( 'hello' )
        self.assertEqual( 'echo hello', command.preview() )

        command = Command( 'echo' )
        command.add_args( hello='hello' )
        self.assertEqual( 'echo hello hello', command.preview() )


class Echo( Command ):
    command = 'echo'
    delegate = None


class Echo_with_delegate( Command ):
    command = 'echo'
    delegate = System_run


class Test_delegate( TestCase ):
    def setUp( self ):
        self.command_without_delegate = Echo
        self.command = Echo_with_delegate
        self.delegate_preview = System_run().preview()
        self.exist_unit = Command_json_result(
            '[{"unit": "chibi_echo"}]', '', 0 )
        self.not_exist_unit = Command_json_result(
            '[{"unit": "chibi_echo"}]', '', 0 )

    def test_should_work_without_delegate( self ):
        preview = self.command_without_delegate().preview()
        self.assertEqual( "echo", preview )

    def test_should_work_with_delegate( self ):
        preview = self.command().preview()
        delegate_preview = self.command().prepare_delegate().preview()
        self.assertEqual(
            f"{delegate_preview} echo", preview )

    def test_when_the_unit_exist_should_add_random_str( self ):
        with patch.object( Systemctl, 'run' ) as run:
            run.return_value = self.exist_unit
            command = self.command()
            preview = command.preview()
        expected = (
            r'systemd-run --unit=chibi_echo_.{4} --property=Delegate=yes '
            r'--user --scope echo'
        )
        result = re.match( expected, preview )
        self.assertTrue( result )
