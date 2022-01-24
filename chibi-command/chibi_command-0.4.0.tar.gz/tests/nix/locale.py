from unittest import TestCase

from chibi_command.nix import Localectl


class Test_iptables( TestCase ):
    def test_set_locale_es_mx( self ):
        result = Localectl.set_locale( 'es_MX.utf8' )
        self.assertEqual(
            "localectl set-locale LANG=es_MX.utf8", result.preview() )
