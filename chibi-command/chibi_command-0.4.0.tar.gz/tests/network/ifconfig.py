from unittest import TestCase

from chibi_command.network.ifconfig import Ifconfig


class Test_iwconfig( TestCase ):
    def test_should_build_up( self ):
        preview = Ifconfig.interface( 'wlan0' ).up().preview()
        self.assertEqual( preview, 'ifconfig wlan0 up' )

    def test_should_build_down( self ):
        preview = Ifconfig.interface( 'wlan0' ).down().preview()
        self.assertEqual( preview, 'ifconfig wlan0 down' )
