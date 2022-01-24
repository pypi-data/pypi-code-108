from unittest import TestCase
import copy

from chibi.atlas import Chibi_atlas
from chibi_command import Command
from chibi_command import Command_result
from chibi_command.nix.systemd_run import System_run
from chibi_command.nix.systemd import Journal_status, Journal_show


class Test_systemd_run( TestCase ):
    def test_should_work( self ):
        result = System_run().preview()
        self.assertEqual(
            result,
            ( f'systemd-run --unit={System_run.kw["unit"]} '
            '--property=Delegate=yes --user --scope' ) )

    def test_set_command( self ):
        result = System_run( 'lxc-ls', '-f' )
        self.assertEqual(
            result,
            ( f'systemd-run --unit={System_run.kw["unit"]} '
            '--property=Delegate=yes --user --scope lxc-ls -f' ) )
