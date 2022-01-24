from chibi_command import Command
from chibi_hybrid.chibi_hybrid import Chibi_hybrid


class Sysctl( Command ):
    command = 'sysctl'
    captive = False

    @Chibi_hybrid
    def write( cls, namespace, value ):
        return cls( '-w', f'{namespace}={value}')

    @write.instancemethod
    def write( self, namespace, value ):
        self.add_args( '-w', f'{namespace}={value}')
        return self
