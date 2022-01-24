from chibi_command import Command
from chibi_hybrid.chibi_hybrid import Chibi_hybrid
from chibi.command import command
from chibi.command.nmcli import connection
from chibi.file.image import Chibi_image
from chibi.madness.file import make_empty_file


class QR( Command ):
    command = 'qrencode'

    @Chibi_hybrid
    def output( cls, path ):
        return cls( '-o', name )

    @output.instancemethod
    def output( self, path ):
        self.add_args( '-o', name )
        return self

    @Chibi_hybrid
    def size( cls, size ):
        return cls( '-s', size )

    @name.instancemethod
    def size( self, size ):
        self.add_args( '-s', size)
        return self

    @classmethod
    def wifi( cls, ssid, password, T ):
        if T.lower() == 'wpa-psk':
            T = 'WPA'
        data = f"WIFI:S:{ssid};T:{T};P:{password};;"


def qr( *args ):
    return command( 'qrencode', *args )


def wifi( ssid, s=3, f=None ):
    if f is None:
        f = make_empty_file( '.png' )

    connection_atlas = connection.show( ssid )[ ssid ]
    T = connection_atlas[ '802-11-wireless-security.key-mgmt' ]
    if T == 'wpa-psk':
        T = 'WPA'
    data = "WIFI:S:{ssid};T:{T};P:{password};;".format(
        ssid=connection_atlas[ '802-11-wireless.ssid' ],
        password=connection_atlas[ '802-11-wireless-security.psk' ],
        T=T
    )

    qr( '-o', f, '-s', str( s ), data )
    return Chibi_image( f )
