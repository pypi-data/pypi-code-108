from chibi_command import Command


class Mariadb( Command ):
    command = 'mysql'
    captive = False

    @classmethod
    def user( cls, user ):
        return cls( '-u', user )

    def password( self, password ):
        self.add_args( '-p{}'.format( password ) )
        return self

    def run_script( self, script ):
        return self( stdin=script )


class Mysql( Mariadb ):
    pass
