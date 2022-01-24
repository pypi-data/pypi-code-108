from chibi_command import Command
from chibi_hybrid.chibi_hybrid import Chibi_hybrid


class Xfconf_query( Command ):
    command = 'xfconf-query'
    captive = False

    @Chibi_hybrid
    def channel( cls, channel ):
        return cls( '-c', channel )

    @channel.instancemethod
    def channel( cls, channel ):
        self.add_args( '-c', channel )
        return self

    @Chibi_hybrid
    def prop( cls, prop ):
        return cls( '-p', prop )

    @prop.instancemethod
    def prop( self, prop ):
        self.add_args( '-p', prop )
        return self

    @Chibi_hybrid
    def save( cls, value ):
        return cls( '-s', value )

    @save.instancemethod
    def save( self, value ):
        self.add_args( '-s', value )
        return self
