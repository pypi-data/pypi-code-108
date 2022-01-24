from chibi.madness.file import make_empty_file

from chibi_command import Command


class QR_encode( Command ):
    command = 'qrencode'

    @classmethod
    def wifi( cls, ssid, T, password, s=3, output_file=None ):
        if output_file is None:
            output_file = make_empty_file( '.png' )

        #connection_atlas = connection.show( ssid )[ ssid ]
        #T = connection_atlas[ '802-11-wireless-security.key-mgmt' ]
        if T == 'wpa-psk':
            T = 'WPA'
        data = "WIFI:S:{ssid};T:{T};P:{password};;".format(
            ssid=connection_atlas[ '802-11-wireless.ssid' ],
            password=connection_atlas[ '802-11-wireless-security.psk' ],
            T=T
        )
        return cls( '-o', output_file, '-s', str( s ), data )
