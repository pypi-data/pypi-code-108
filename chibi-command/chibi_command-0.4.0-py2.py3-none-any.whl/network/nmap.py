from chibi_command import Command
from chibi.atlas import loads
from chibi.snippet.xml import guaranteed_list

from chibi_command import Command_result


class Nmap_result( Command_result ):
    def parse_result( self ):
        result = loads( self.result )
        result = guaranteed_list( result, 'host' )
        self.result = result



class Nmap( Command ):
    command = 'nmap'
    args = ( '-oX', '-' )
    captive = True
    result_class=Nmap_result
