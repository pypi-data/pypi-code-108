import json

from chibi.atlas import Chibi_atlas

from chibi_command import Command, Command_result
from chibi_command.nix import Systemctl
from chibi_hybrid.chibi_hybrid import Chibi_hybrid
from chibi.madness.string import generate_string


__all__ = [ 'Systemctl' ]


class System_run( Command ):
    command = 'systemd-run'
    captive = False
    args = [ '--user', '--scope', ]
    kw = { 'unit': 'chibi_command_delegate', 'property': 'Delegate=yes' }
    kw_format = "--{key}={value}"

    @Chibi_hybrid
    def set_command( cls, command, *args ):
        command = cls( command, *args )
        return command

    @set_command.instancemethod
    def set_command( self, command, *args ):
        self.add_args( command, *args )
        return self

    def build_kw( self, **kw ):
        units = Systemctl.list_units().run()
        exists_unit = (
            x[ 'unit' ].startswith( self.kw[ 'unit' ] ) for x in units )
        if any( exists_unit ):
            unit_name = self.kw[ 'unit' ]
            extra = generate_string( 4 )
            self.kw[ 'unit' ] = f"{unit_name}_{extra}"
        return super().build_kw( **kw )
