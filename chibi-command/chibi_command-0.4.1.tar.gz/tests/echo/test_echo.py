from unittest import TestCase

from chibi_command.echo import Echo, Cowsay, CirnoSay, Ponysay
from chibi_command import Command_result


class Test_echo( TestCase ):
    def setUp( self ):
        self.hello = 'hello world'
        self.command = Echo( captive=True )

    def test_should_run_using_call( self ):
        r = self.command( self.hello )
        self.assertIsInstance( r, Command_result )

    def test_should_run_using_run( self ):
        r = self.command.run( self.hello )
        self.assertIsInstance( r, Command_result )

    def test_should_have_the_output( self ):
        r = self.command( self.hello )
        self.assertTrue( r.result )
        self.assertEqual( r.return_code, 0 )
        self.assertFalse( r.error )

    def test_mock( self ):
        r = self.command.preview( self.hello )
        self.assertEqual(
            "{} {}".format( self.command.command, self.hello ), r )

    def test_stdin( self ):
        r = self.command( stdin=self.hello )
        self.assertTrue( r.result )
        self.assertEqual( r.return_code, 0 )
        self.assertFalse( r.error )


class Test_cowsay( Test_echo ):
    def setUp( self ):
        super().setUp()
        self.command = Cowsay( captive=True)


class Test_ponysay( Test_echo ):
    def setUp( self ):
        super().setUp()
        self.command = Ponysay( captive=True )


class Test_cirnosay( Test_echo ):
    def setUp( self ):
        super().setUp()
        self.command = CirnoSay( captive=True )
