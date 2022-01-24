from extools.view import exview
from extools.view import ExViewError

def conversion_factor_for(uom):
    try:
        with exview("IC0746", seek_to={'UNIT': uom}) as exv:
            return exv.get("DEFCONV")
    except ExViewError:
        return 1

