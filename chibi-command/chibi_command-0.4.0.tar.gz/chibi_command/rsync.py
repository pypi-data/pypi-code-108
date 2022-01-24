from chibi_hybrid.chibi_hybrid import Chibi_hybrid

from chibi_command import Command


class Rsync( Command ):
    command = 'rsync'
    captive = False

    @Chibi_hybrid
    def options( cls, *options ):
        return cls( *options )

    @options.instancemethod
    def options( self, *options ):
        self.add_args( *options )
        return self

    @Chibi_hybrid
    def archive_mode( cls ):
        return cls.options( '-a' )

    @archive_mode.instancemethod
    def archive_mode( self ):
        self.options( '-a' )
        return self

    @Chibi_hybrid
    def verbose( cls ):
        return cls.options( '-v' )

    @verbose.instancemethod
    def verbose( self ):
        self.options( '-v' )
        return self

    @Chibi_hybrid
    def compress( cls ):
        return cls.options( '-z' )

    @compress.instancemethod
    def compress( self ):
        self.options( '-z' )
        return self

    @Chibi_hybrid
    def update( cls ):
        return cls.options( '-u' )

    @update.instancemethod
    def update( self ):
        self.options( '-u' )
        return self

    @Chibi_hybrid
    def human( cls ):
        return cls.options( '-h' )

    @human.instancemethod
    def human( self ):
        self.options( '-h' )
        return self

    @Chibi_hybrid
    def progress( cls ):
        return cls.options( '--progress' )

    @progress.instancemethod
    def progress( self ):
        self.options( '--progress' )
        return self

    @Chibi_hybrid
    def update( cls ):
        return cls.options( '-u' )

    @update.instancemethod
    def update( self ):
        self.options( '-u' )
        return self

    @Chibi_hybrid
    def ignore( cls ):
        return cls.options( '-I' )

    @update.instancemethod
    def ignore( self ):
        self.options( '-I' )
        return self

    @Chibi_hybrid
    def clone_dir( cls ):
        instance = cls.archive_mode()
        instance.update()
        return instance

    @clone_dir.instancemethod
    def clone_dir( self ):
        self.archive_mode().update()
        return self
