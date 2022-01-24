from unittest import TestCase

from chibi_command.network.interfaces import Ip, Iw
from chibi_command.network.interfaces import Network, Interface


class Test_interface( TestCase ):
    def test_up_should_create_the_command_with_up( self ):
        interface = Interface( name='wlan0' )
        command = interface.up()
        self.assertEqual( command.preview(), 'ifconfig wlan0 up' )

    def test_down_should_create_the_command_with_down( self ):
        interface = Interface( name='wlan0' )
        command = interface.down()
        self.assertEqual( command.preview(), 'ifconfig wlan0 down' )

    def test_set_momnitor_should_create_the_command( self ):
        interface = Interface( name='wlan0' )
        command = interface.set_monitor()
        self.assertEqual(
            command.preview(), 'iwconfig wlan0 mode monitor' )

    def test_set_manager_should_create_the_command( self ):
        interface = Interface( name='wlan0' )
        command = interface.set_manager()
        self.assertEqual(
            command.preview(), 'iwconfig wlan0 mode manager' )


class Test_ip_commnad( TestCase ):
    def test_addr_should_work( self ):
        c = Ip.addr()
        preview = c.preview()
        self.assertEqual( preview, 'ip addr' )

    def test_should_return_interface_class( self ):
        result = Ip.addr().run()
        self.assertTrue( result )
        interfaces = result.result
        self.assertIsInstance( interfaces, Network )
        for interface in interfaces.values():
            self.assertIsInstance( interface, Interface )

    def test_each_interface_should_have_their_name( self ):
        result = Ip.addr().run()
        self.assertTrue( result )
        interfaces = result.result
        for name, interface in interfaces.items():
            self.assertEqual( name, interface.name )


class Test_iw_command( TestCase ):
    def test_iw_dev_should_work( self ):
        c = Iw.dev()
        self.assertEqual( c.preview(), 'iw dev' )

    def test_iw_with_interface_should_work( self ):
        c = Iw.dev().interface( 'wlan0' )
        self.assertEqual( c.preview(), 'iw dev wlan0' )

    def test_iw_set_channel_should_work( self ):
        c = Iw.dev().interface( 'wlan0' ).set_channel( 10 )
        self.assertEqual( c.preview(), 'iw dev wlan0 set channel 10' )
