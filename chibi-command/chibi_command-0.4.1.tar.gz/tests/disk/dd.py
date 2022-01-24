from unittest import TestCase

from chibi_command.disk.dd import DD


class Test_dd( TestCase ):
    def test_dd( self ):
        dd = DD.input_file( '/dev/sda' )
        self.assertEqual(
            dd.preview(), 'dd bs=1M status=progress if=/dev/sda' )
        dd.output_file( '~/sda.img' )
        self.assertEqual(
            dd.preview(), 'dd bs=1M status=progress if=/dev/sda of=~/sda.img' )

        dd = DD.output_file( '/dev/sda' )
        self.assertEqual(
            dd.preview(), 'dd bs=1M status=progress of=/dev/sda' )
        dd.input_file( '~/sda.img' )
        self.assertEqual(
            dd.preview(), 'dd bs=1M status=progress of=/dev/sda if=~/sda.img' )

    def test_to_zero( self ):
        dd = DD.to_zero( '/dev/sda' )
        self.assertEqual(
            dd.preview(), 'dd bs=1M status=progress if=/dev/zero of=/dev/sda' )
