from chibi_hybrid.chibi_hybrid import Chibi_hybrid

from chibi_command import Command


__all__ = [ 'Localectl' ]


class Localectl( Command ):
    command = 'localectl'

    @Chibi_hybrid
    def set_locale( cls, lang ):
        return cls( 'set-locale', f'LANG={lang}' )

    @set_locale.instancemethod
    def set_locale( self, lang ):
        self.add_args( 'set-locale', f'LANG={lang}' )
