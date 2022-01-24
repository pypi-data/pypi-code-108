from chibi_command import Command


class MPC( Command ):
    command = 'mpc'

    @classmethod
    def pause( cls ):
        return cls( 'pause' )()

    @classmethod
    def stop( cls ):
        return cls( 'stop' )()

    @classmethod
    def play( cls ):
        return cls( 'play' )()

    @classmethod
    def play_toggle( cls ):
        return cls( 'toggle' )()

    @classmethod
    def next( cls ):
        return cls( 'next' )()

    @classmethod
    def prev( cls ):
        return cls( 'prev' )()
