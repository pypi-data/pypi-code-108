from unittest import TestCase

from chibi_command.network.iwconfig import Iwconfig


class Test_iwconfig( TestCase ):
    def test_should_build_monitor( self ):
        preview = Iwconfig.interface( 'wlan0' ).set_monitor().preview()
        self.assertEqual( preview, 'iwconfig wlan0 mode monitor' )

    def test_should_build_manager( self ):
        preview = Iwconfig.interface( 'wlan0' ).set_manager().preview()
        self.assertEqual( preview, 'iwconfig wlan0 mode manager' )
