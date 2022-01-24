from unittest import TestCase

from chibi.atlas import Chibi_atlas

from chibi_command.lxc import lxc
from chibi_command.lxc import delegate as lxc_delegate
from chibi_command.nix import Systemctl
from chibi_command.nix.systemd_run import System_run


class Test_lxc_create( TestCase ):

    def test_name_return_instance( self ):
        c = lxc.Create()
        c2 = c.name( 'test' )
        self.assertIs( c, c2 )

    def test_template_return_instance( self ):
        c = lxc.Create()
        c2 = c.template( 'test' )
        self.assertIs( c, c2 )


class Test_lxc_attach( TestCase ):

    def test_add_double_dash_in_end( self ):
        preview = lxc.Attach.name( 'test' ).preview( 'some_command' )
        self.assertEqual(
            preview, 'lxc-attach --clear-env -n test -- some_command' )

    def test_name_return_instance( self ):
        c = lxc.Attach()
        c2 = c.name( 'test' )
        self.assertIs( c, c2 )

    def test_set_var_class( self ):
        c = lxc.Attach.set_var( 'test', 'asdf' )
        self.assertEqual(
            c.preview(),
            "lxc-attach --clear-env --set-var test=asdf --")

    def test_set_var_instance( self ):
        c = lxc.Attach()
        c.set_var( 'test', 'asdf' )
        self.assertEqual(
            c.preview(),
            "lxc-attach --clear-env --set-var test=asdf --")

    def test_when_run_a_chibi_command_should_be_sended_to_the_contaner( self ):
        command = Systemctl.status( 'unknow' )
        result = lxc.Attach().name( 'some one' ).preview( command )
        self.assertEqual(
            'lxc-attach --clear-env -n some one '
            '-- systemctl --output=json status unknow',
            result )


class Test_lxc_info:
    def test_should_do_the_format( self ):
        self.assertIsInstance( self.info.result, Chibi_atlas )


class Test_lxc_info_stopped( Test_lxc_info, TestCase ):
    def setUp( self ):
        self.example = """
            Name:           quetzalcoatl\nState:          STOPPED\n
        """
        self.info = lxc.Info_result( self.example, '', 0 )

    def test_result_should_process_the_state( self ):
        self.assertFalse( self.info.is_running )


class Test_lxc_info_running( Test_lxc_info, TestCase ):
    def setUp( self ):
        super().setUp()
        self.example = """Name:           quetzalcoatl
            State:          RUNNING
            PID:            7198
            IP:             192.168.122.49
            CPU use:        270973560504
            BlkIO use:      607961088
            Memory use:     226648064
            KMem use:       0
            Link:           veth7QE74S
            TX bytes:      1398585
            RX bytes:      192296828
            Total bytes:   193695413
        """
        self.info = lxc.Info_result( self.example, '', 0 )

    def test_result_should_process_the_state( self ):
        self.assertTrue( self.info.is_running )


class Test_lxc_delegate_create( TestCase ):
    def setUp( self ):
        self.lxc = lxc_delegate

    def test_name_return_instance( self ):
        c = self.lxc.Create()
        c2 = c.name( 'test' )
        self.assertIs( c, c2 )

    def test_template_return_instance( self ):
        c = self.lxc.Create()
        c2 = c.template( 'test' )
        self.assertIs( c, c2 )


class Test_lxc_delegate_attach( TestCase ):
    def setUp( self ):
        self.lxc = lxc_delegate
        self.delegate_preview = System_run().preview()

    def test_add_double_dash_in_end( self ):
        preview = self.lxc.Attach.name( 'test' ).preview( 'some_command' )
        delegate_preview = self.lxc.Attach().prepare_delegate().preview()
        self.assertEqual(
            preview,
            ( f'{delegate_preview} lxc-attach --clear-env'
            ' -n test -- some_command' ) )

    def test_name_return_instance( self ):
        c = self.lxc.Attach()
        c2 = c.name( 'test' )
        self.assertIs( c, c2 )

    def test_set_var_class( self ):
        c = self.lxc.Attach.set_var( 'test', 'asdf' )
        delegate_preview = self.lxc.Attach().prepare_delegate().preview()
        self.assertEqual(
            c.preview(),
            ( f"{delegate_preview} lxc-attach --clear-env --set-var"
            " test=asdf --" ) )

    def test_set_var_instance( self ):
        c = self.lxc.Attach()
        c.set_var( 'test', 'asdf' )
        delegate_preview = self.lxc.Attach().prepare_delegate().preview()
        self.assertEqual(
            c.preview(),
            ( f"{delegate_preview} lxc-attach --clear-env "
            "--set-var test=asdf --" ) )

    def test_when_run_a_chibi_command_should_be_sended_to_the_contaner( self ):
        command = Systemctl.status( 'unknow' )
        result = self.lxc.Attach().name( 'some one' )
        result = result.preview( command )
        delegate_preview = self.lxc.Attach().prepare_delegate().preview()
        self.assertEqual(
            f'{delegate_preview} lxc-attach --clear-env -n some one '
            '-- systemctl --output=json status unknow',
            result )
