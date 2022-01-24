from chibi.atlas import Chibi_atlas
from chibi_command import Command, Command_result


class Connection_detail( Chibi_atlas ):
    @property
    def detail( self ):
        try:
            return self._detail
        except AttributeError:
            detail = NMcli.connection_detail( self.name )
            if detail:
                self._detail = detail.result
            else:
                raise NotImplementedError(
                    'sin implementar cuando tiene un error' )
            return self._detail


class Connections( Command_result ):
    def parse_result( self ):
        rows = self.result.split( '\n' )
        self.result = []
        for r in rows:
            if not r:
                continue
            r = r.split( ':' )
            d = r[3] if r[3] else None
            self.result.append(
                Connection_detail(
                    name=r[0], uuid=r[1], kind=r[2], device=d ) )


class Connection_result_detail( Command_result ):
    def parse_result( self ):
        rows = self.result.split( '\n' )
        d = dict( ( tuple( r.rsplit( ':', 1 ) ) for r in rows if r ) )
        self.result = Chibi_atlas( d )


class NMcli( Command ):
    command = 'nmcli'
    args = ( '-t', )
    captive = True

    @classmethod
    def current( cls ):
        connections = cls(
            'connection', 'show', '--show-secrets', '--active',
            result_class=Connections )()
        if connections:
            return connections.result[0]

    @classmethod
    def connections( cls ):
        connections = cls(
            'connection', 'show', '--show-secrets',
            result_class=Connections )()
        return connections

    @classmethod
    def connection_detail( cls, connection ):
        connection = cls(
            'connection', 'show', '--show-secrets', connection,
            result_class=Connection_result_detail )()
        return connection
