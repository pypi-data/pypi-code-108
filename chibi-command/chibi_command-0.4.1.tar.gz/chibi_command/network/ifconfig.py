from chibi_hybrid.chibi_hybrid import Chibi_hybrid
from chibi_command import Command


class Ifconfig( Command ):
    command = 'ifconfig'
    captive = False

    @Chibi_hybrid
    def interface( cls, interface ):
        if isinstance( interface, str ):
            return cls( interface )
        return cls( interface.name )

    @interface.instancemethod
    def interface( self, interface ):
        if isinstance( interface, str ):
            self.add_args( interface )
        else:
            self.add_args( interface.name )
        return self

    def up( self ):
        self.add_args( 'up' )
        return self

    def down( self ):
        self.add_args( 'down' )
        return self
