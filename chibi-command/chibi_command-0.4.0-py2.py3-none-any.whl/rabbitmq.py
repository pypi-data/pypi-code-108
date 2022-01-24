from chibi_command import Command


class Rabbitmqctl( Command ):
    command = 'rabbitmqctl'
    captive = False

    @classmethod
    def add_user( cls, user, password ):
        return cls( 'add_user', user, password )()

    @classmethod
    def delete_user( cls, user ):
        return cls( 'delete_user', user )()

    @classmethod
    def set_user_tags( cls, user, tag ):
        return cls( 'set_user_tags', user, tag )()

    @classmethod
    def set_permissions( cls, vhost, user, conf='.*', write='.*', read='.*' ):
        return cls( 'set_permissions', '-p', vhost, user, conf, write, read )()

    @classmethod
    def add_vhost( cls, vhost ):
        return cls( 'add_vhost', vhost )()

    @classmethod
    def list_user( cls ):
        return cls( 'list_users', captive=True )()
