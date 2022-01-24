import json

from chibi.atlas import Chibi_atlas

from chibi_command import Command, Command_result, Command_json_result


__all__ = [ 'Systemctl' ]


class Journal_status( Command_result ):
    def __init__( self, result, error, return_code ):
        super().__init__( result, error, return_code )
        pre_parse = self.result.split( '\n' )
        end_of_status = pre_parse.index( '' )

        status = pre_parse[ :end_of_status ]
        pre_messages = pre_parse[ end_of_status:]
        messages = [ json.loads( m ) for m in pre_messages if m ]
        if status:
            service = status[0].split()[1]
        else:
            service = ''

        if service:
            show = Systemctl.show( service ).run().result
        else:
            show = Chibi_atlas()
        self.result = Chibi_atlas(
            service=service, human=status, messages=messages,
            properties=show )


class Journal_show( Command_result ):
    def __init__( self, result, error, return_code ):
        super().__init__( result, error, return_code )
        pre_parse = self.result.split( '\n' )

        result = {}
        for pre in pre_parse:
            if pre:
                k, v = pre.rsplit( '=', 1 )
                result[ k.strip() ] = v.strip()

        self.result = Chibi_atlas( result )


class Systemctl( Command ):
    command = 'systemctl'
    captive = True
    kw = { '--output': 'json' }
    kw_format = "{key}={value}"
    result_class = Journal_status

    @classmethod
    def status( cls, *services ):
        result = cls( 'status', *services )
        return result

    @classmethod
    def start( cls, *services ):
        result = cls( 'start', *services )
        return result

    @classmethod
    def enable( cls, *services ):
        result = cls( 'enable', *services )
        return result

    @classmethod
    def restart( cls, *services ):
        result = cls( 'restart', *services )
        return result

    @classmethod
    def daemon_reload( cls ):
        result = cls( 'daemon-reload' )
        return result

    @classmethod
    def show( cls, *services ):
        return cls( 'show', *services, result_class=Journal_show )

    @classmethod
    def list_units( cls ):
        return cls( 'list-units', '--global', result_class=Command_json_result )
