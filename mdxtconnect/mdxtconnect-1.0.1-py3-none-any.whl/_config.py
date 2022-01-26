""" Configuration storage/retrieval for the MDXT Connect API """

import os
import json
from itertools import cycle

class Config:
    def __init__( self ):
        self.config = { 'username': '', 'passkey': '', 'url': None }
        self.filename = os.path.expanduser( '~/mdxtconnect.json' )

    def read( self ):
        good = True
        msg = ''

        try:
            with open( self.filename, 'r' ) as file:
                config = json.load( file )

            passkey = config.get( 'passkey' )
            if isinstance( passkey, list ):
                temp = ''
                for code, mask in zip( passkey, cycle( self.filename ) ):
                    temp += chr( code ^ ord( mask ) )
                config[ 'passkey' ] = temp
                self.config = config

            elif isinstance( passkey, str ):
                self.config = config
                self.write()

            msg = f'Successfully read configuration from {self.filename}'

        except (OSError, IOError):
            good = False
            msg = f'Failed to read configuration from file {self.filename}'

        return (good, msg)

    def write( self ):
        config = self.config.copy()
        passkey = config.get( 'passkey' )

        if isinstance( passkey, str ):
            temp = []
            for code, mask in zip( passkey, cycle( self.filename ) ):
                temp.append( ord( code ) ^ ord( mask ) )
            config[ 'passkey' ] = temp

        good = True
        msg = ''

        try:
            with open( self.filename, 'w' ) as file:
                json.dump( config, file )

            msg = f'Successfully wrote configuration to {self.filename}'

        except (OSError, IOError):
            good = False
            msg = f'Failed to write file {self.filename}'

        return (good, msg)

    def set( self, username, passkey, url ):
        changed = False

        if isinstance( username, str ):
            self.config[ 'username' ] = username
            changed = True

        if isinstance( passkey, str ):
            self.config[ 'passkey' ] = passkey
            changed = True

        if isinstance( url, str ):
            self.config[ 'url' ] = url
            changed = True

        return changed

    def get_username( self ):
        return self.config[ 'username' ]

    def get_passkey( self ):
        return self.config[ 'passkey' ]

    def get_url( self ):
        url = None

        if self.config.get( 'url' ):
            url = self.config[ 'url' ]

        return url
