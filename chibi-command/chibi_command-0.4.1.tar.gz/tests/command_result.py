import copy
from unittest import TestCase
from chibi_command import Command_result, Command_json_result
from chibi.atlas import Chibi_atlas


class Test_result( TestCase ):
    def test_when_return_code_is_1_should_be_false( self ):
        result = Command_result( '', '', 1, )
        self.assertFalse( result )

    def test_when_return_code_is_0_should_be_true( self ):
        result = Command_result( '', '', 0, )
        self.assertTrue( result )


class Test_result_json( TestCase ):
    def test_on_send_json_should_be_chibi_atlas( self ):
        result = Command_json_result( '{"asdf":"zxcv"}', '', 0, )
        self.assertIsInstance( result.result, Chibi_atlas )

    def test_should_containt_the_expected_keys( self ):
        result = Command_json_result( '{"asdf":"zxcv"}', '', 0, )
        expected = { 'asdf': 'zxcv' }
        self.assertEqual( result.result, expected )
