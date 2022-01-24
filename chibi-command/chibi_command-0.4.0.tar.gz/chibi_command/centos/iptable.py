from chibi_hybrid.chibi_hybrid import Chibi_hybrid
from chibi_command import Command


__all__ = [ 'Iptables', 'Firewall_cmd' ]


class Iptables( Command ):
    command = "iptables"
    kw_format = "--{key} {value}"


    @Chibi_hybrid
    def table( cls, table ):
        return cls( table=table )

    @table.instancemethod
    def table( self, table ):
        self.add_args( table=table )
        return self

    @Chibi_hybrid
    def append( cls, chain ):
        return cls( append=chain )

    @append.instancemethod
    def append( self, chain ):
        self.add_args( append=chain )
        return self

    @Chibi_hybrid
    def list ( cls, chain=None ):
        if chain:
            return cls( '--list', chain )
        return cls( '--list' )

    @list.instancemethod
    def list( self, chain, ):
        if chain:
            self.add_args( '--list', chain, )
        else:
            self.add_args( '--list', )
        return self

    @Chibi_hybrid
    def delete( cls, chain=None, rule=None ):
        command = cls( '--delete', )
        if chain:
            command.add_args( chain )
        if rule:
            command.add_args( rule )
        return command

    @delete.instancemethod
    def delete( self, chain=None, rule=None ):
        self.add_args( '--delete', )
        if chain:
            self.add_args( chain )
        if rule:
            self.add_args( rule )
        return self

    @Chibi_hybrid
    def line_numbers( cls ):
        return cls( '--line-numbers' )

    @line_numbers.instancemethod
    def line_numbers( self ):
        self.add_args( '--line-numbers' )
        return self

    @Chibi_hybrid
    def protocol( cls, protocol ):
        return cls( protocol=protocol )

    @protocol.instancemethod
    def protocol( self, protocol ):
        self.add_args( protocol=protocol )
        return self

    @Chibi_hybrid
    def in_interface( cls, interface ):
        return cls( **{ 'in-interface': interface } )

    @in_interface.instancemethod
    def in_interface( self, interface ):
        kw = { 'in-interface': interface }
        self.add_args( **kw )
        return self

    @Chibi_hybrid
    def destination_port( cls, port ):
        return cls( **{ 'destination-port': port } )

    @destination_port.instancemethod
    def destination_port( self, port ):
        kw = { 'destination-port': port }
        self.add_args( **kw )
        return self

    @Chibi_hybrid
    def jump( cls, target ):
        return cls( jump=target )

    @destination_port.instancemethod
    def jump( self, target ):
        self.add_args( jump=target )
        return self

    @Chibi_hybrid
    def to_destination( cls, ip, port=None ):
        if port is not None:
            ip = f"{ip}:{port}"
        return cls( **{ 'to-destination': port } )

    @to_destination.instancemethod
    def to_destination( self, ip, port=None):
        if port is not None:
            ip = f"{ip}:{port}"

        kw = { 'to-destination': ip }
        self.add_args( **kw )
        return self


class Firewall_cmd( Command ):
    command = "firewall-cmd"

    @classmethod
    def reload( cls ):
        """
        """
        result = cls( '--reload' )()
        return result

    @classmethod
    def add_port( cls, ports, kind='tcp', permanent=True ):
        """
        agrega un puerto usando firewall-cmd

        Parameters
        ==========
        ports: str
            formato de puertos puede ser el numero o un rango
            25672, 5671-5672
        kind: str
            tipo del puerto tcp o udp
        permanent: bool
        """
        if not permanent:
            raise NotImplementedError
        else:
            permanent = '--permanent'
        return cls( permanent, "--add-port={}/{}".format( ports, kind ) )
