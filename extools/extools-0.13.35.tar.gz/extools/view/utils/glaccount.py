from extools.view import exview
from extools.view import ExViewError

def formatted_account_number_for(unfmtacct):
    try:
        with exview("GL0001", seek_to={'ACCTID': unfmtacct}) as exv:
            return exv.get("ACCTFMTTD")
    except ExViewError:
        return unfmtacct


