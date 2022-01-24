from unittest import TestCase
from chibi_command.centos import Iptables


class Test_iptables( TestCase ):
    def test_table( self ):
        result = Iptables.table( 'nat' )
        self.assertEqual(
            "iptables --table nat", result.preview() )

    def test_list( self ):
        result = Iptables.list()
        self.assertEqual(
            "iptables --list", result.preview() )

    def test_append( self ):
        result = Iptables.table( 'nat' ).append( "PREROUTING" )
        self.assertEqual(
            "iptables --table nat --append PREROUTING", result.preview() )

    def test_protocol( self ):
        result = Iptables.table( 'nat' ).append( "PREROUTING" ).protocol( 'tcp' )
        self.assertEqual(
            "iptables --table nat --append PREROUTING --protocol tcp", result.preview() )

    def test_protocol_tcp( self ):
        result = Iptables.table( 'nat' ).append( "PREROUTING")
        result = result.protocol( 'tcp' )
        result.in_interface( 'eth1' )
        self.assertEqual(
            "iptables --table nat --append PREROUTING --protocol tcp --in-interface eth1",
            result.preview() )

    def test_destination_port( self ):
        result = Iptables.table( 'nat' ).append( "PREROUTING")
        result = result.protocol( 'tcp' )
        result.in_interface( 'eth1' ).destination_port( 8000 )
        self.assertEqual(
            "iptables --table nat --append PREROUTING --protocol tcp --in-interface eth1"
            " --destination-port 8000",
            result.preview() )

    def test_jump( self ):
        result = Iptables.table( 'nat' ).append( "PREROUTING")
        result = result.protocol( 'tcp' )
        result.in_interface( 'eth1' ).destination_port( 8000 ).jump( 'DNAT' )
        self.assertEqual(
            "iptables --table nat --append PREROUTING --protocol tcp --in-interface eth1"
            " --destination-port 8000 --jump DNAT",
            result.preview() )

    def test_to_destination( self ):
        result = Iptables.table( 'nat' ).append( "PREROUTING")
        result = result.protocol( 'tcp' )
        result.in_interface( 'eth1' ).destination_port( 8000 ).jump( 'DNAT' )
        result.to_destination( "127.0.0.1", 8000 )
        self.assertEqual(
            "iptables --table nat --append PREROUTING --protocol tcp --in-interface eth1"
            " --destination-port 8000 --jump DNAT "
            "--to-destination 127.0.0.1:8000",
            result.preview() )

    def test_delete( self ):
        result = Iptables.table( 'nat' ).delete()
        self.assertEqual(
            "iptables --table nat --delete", result.preview() )
