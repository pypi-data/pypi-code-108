from chibi.file import Chibi_file
from chibi.atlas import Chibi_atlas
from chibi_donkey.donkey import Donkey

donkey = Donkey( separator='.' )


class Chibi_lxc_config( Chibi_file ):
    def read( self ):
        data = super().read()
        result = Chibi_atlas()
        for line in data.split( '\n' ):
            line = line.strip()
            if line.startswith( '#' ) or not line:
                continue
            rule, value = line.split( '=', 1 )
            rule = rule.strip()
            value = value.strip()
            try:
                current = donkey.get( rule, result )
                if not isinstance( current, list ):
                    current = [ current ]
            except KeyError:
                current = None
            if current is None:
                donkey.setter( rule, result, value )
            else:
                current.append( value )
                donkey.setter( rule, result, current )
        return result

    def write( self, value ):
        if not isinstance( value, dict ):
            raise TypeError( f"se experaba un typo dict y no {type( value )}" )
        compress = donkey.compress( value )
        lines = []
        for k, v in compress.items():
            if isinstance( v, list ):
                for vv in v:
                    lines.append( f"{k} = {vv}" )
            else:
                lines.append( f"{k} = {v}" )
        return super().write( "\n".join( lines ) )
