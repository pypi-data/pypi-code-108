from unittest import TestCase
from chibi_command.sysctl import Sysctl


class Test_sysctl_write( TestCase ):

    def test_wrtie_class_shoudl_work( self ):
        expected = 'sysctl -w some.namespace=1000'
        c = Sysctl.write( 'some.namespace', 1000 )
        result = c.preview()
        self.assertEqual( result, expected )

    def test_wrtie_instance_shoudl_work( self ):
        expected = 'sysctl -w some.namespace=1000'
        c = Sysctl().write( 'some.namespace', 1000 )
        result = c.preview()
        self.assertEqual( result, expected )
