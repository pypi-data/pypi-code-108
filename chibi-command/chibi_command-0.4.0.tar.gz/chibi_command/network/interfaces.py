import re

from chibi.atlas import Chibi_atlas
from chibi.snippet import regex
from chibi.snippet.iter import chunk_each
from chibi_hybrid.chibi_hybrid import Chibi_hybrid

from chibi_command import Command_result, Command
from chibi_command.network.ifconfig import Ifconfig
from chibi_command.network.iwconfig import Iwconfig


class Interface( Chibi_atlas ):
    def up( self ):
        return Ifconfig().interface( self.name ).up()

    def down( self ):
        return Ifconfig().interface( self.name ).down()

    def set_monitor( self ):
        return Iwconfig().interface( self.name ).set_monitor()

    def set_manager( self ):
        return Iwconfig().interface( self.name ).set_manager()


class Network( Chibi_atlas ):

    @classmethod
    def load_from_string( cls, s ):
        split = s.split( '\n' )
        interfaces_raw = chunk_each(
            split, lambda x: regex.test( r'^\d+:', x  ) )

        result = cls()
        for interface_raw in interfaces_raw:
            interface_raw = "\n".join( interface_raw )
            interface_name = re.search(
                r"^.*: (?P<interface>\w+.+):",
                interface_raw ).groupdict()[ 'interface' ]
            interface = Interface( name=interface_name )
            result[ interface_name ] = interface

            interface.ip_v4 = re.search(
                r"inet\s*(?P<ip_v4>\d+.\d+.\d+.\d+/\d+)",
                interface_raw, re.MULTILINE )
            if interface.ip_v4:
                interface.ip_v4 = interface.ip_v4.groupdict()[ 'ip_v4' ]

        return result


class Wireless( Network ):
    pass


class Interface_result( Command_result ):
    def parse_result( self ):
        self.result = Network.load_from_string( self.result )


class Ip( Command ):
    command = 'ip'
    captive = True
    result_class=Interface_result

    @Chibi_hybrid
    def addr( cls ):
        return cls( 'addr' )

    @addr.instancemethod
    def addr( self ):
        self.add_args( 'addr' )
        return self


class Iw( Command ):
    command = 'iw'

    @Chibi_hybrid
    def dev( cls ):
        return cls( 'dev' )

    @dev.instancemethod
    def dev( self ):
        self.add_args( 'dev' )
        return self

    @Chibi_hybrid
    def interface( cls, interface ):
        if isinstance( interface, str ):
            return cls( interface )
        return cls( interface.name )

    @interface.instancemethod
    def interface( self, interface ):
        if isinstance( interface, str ):
            self.add_args( interface )
        else:
            self.add_args( interface.name )
        return self

    @Chibi_hybrid
    def set_channel( cls, channel ):
        return cls( 'set', 'channel', channel )

    @set_channel.instancemethod
    def set_channel( self, channel ):
        self.add_args( 'set', 'channel', channel )
        return self
