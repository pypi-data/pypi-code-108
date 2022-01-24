from unittest import TestCase
import copy

from chibi_command import Command
from chibi_command import Command_result
from chibi_command.xfce4 import Xfconf_query


class Test_xfconf_query( TestCase ):
    def test_channel( self ):
        result = Xfconf_query.channel( 'xfce4-desktop' )
        self.assertIsNotNone( result )
        self.assertIsInstance( result, Xfconf_query )
        self.assertEqual( "xfconf-query -c xfce4-desktop", result.preview() )

    def test_prop( self ):
        result = Xfconf_query.prop(
            '/backdrop/screen0/monitorLVDS-1/workspace0/last-image' )
        self.assertIsNotNone( result )
        self.assertIsInstance( result, Xfconf_query )
        self.assertEqual(
            "xfconf-query -p "
            "/backdrop/screen0/monitorLVDS-1/workspace0/last-image",
            result.preview() )

    def test_save( self ):
        result = Xfconf_query.save(
            '/backdrop/screen0/monitorLVDS-1/workspace0/last-image' )
        self.assertIsNotNone( result )
        self.assertIsInstance( result, Xfconf_query )
        self.assertEqual(
            "xfconf-query -s "
            "/backdrop/screen0/monitorLVDS-1/workspace0/last-image",
            result.preview() )

    def test_change_wallpaper( self ):
        result = Xfconf_query.channel( 'xfce4-desktop' )
        result = result.prop(
            '/backdrop/screen0/monitorLVDS-1/workspace0/last-image' )
        result = result.save(
            '/home/user/image.jpg' )
        self.assertIsNotNone( result )
        self.assertIsInstance( result, Xfconf_query )
        self.assertIn( '-c', result.preview() )
        self.assertIn( 'xfconf-query', result.preview() )
        self.assertIn( '-p', result.preview() )
        self.assertIn(
            "/backdrop/screen0/monitorLVDS-1/workspace0/last-image",
            result.preview() )
        self.assertIn( '-s', result.preview() )
        self.assertIn( '/home/user/image.jpg', result.preview() )
