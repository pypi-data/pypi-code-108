from chibi_hybrid.chibi_hybrid import Chibi_hybrid
from chibi_command import Command


class Iwconfig( Command ):
    command = 'iwconfig'
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

    def set_monitor( self ):
        self.add_args( 'mode', 'monitor' )
        return self

    def set_manager( self ):
        self.add_args( 'mode', 'manager' )
        return self
