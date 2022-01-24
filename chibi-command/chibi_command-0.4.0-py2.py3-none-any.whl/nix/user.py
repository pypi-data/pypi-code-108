from chibi.nix import user_exists
from chibi_hybrid.chibi_hybrid import Chibi_hybrid

from chibi_command import Command


__all__ = [ 'User' ]

class User( Command ):
    captive = False

    @Chibi_hybrid
    def name( cls, name ):
        result = cls( name=name )
        return result

    @name.instancemethod
    def name( self, name ):
        self.add_args( name=name )
        return self

    @property
    def create( self ):
        if 'name' in self.kw:
            return Command( 'useradd', self.kw.name )
        raise NotImplementedError(
            "no implementado sin nombre de usuario" )

    @property
    def exists( self ):
        if 'name' in self.kw:
            return user_exists( name=self.kw.name )
        raise NotImplementedError(
            "no implementado sin nombre de usuario" )

    def run( self, *args, **kw ):
        raise NotImplementedError(
            "no se puede ejecutar el comando User" )
