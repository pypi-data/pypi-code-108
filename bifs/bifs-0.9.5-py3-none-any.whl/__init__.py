# Added this file on the theory the import machinery requires it
# to access stuff further down

# in the next line, the first bifs is this package
# bifscore is the file bifscore.py within the package.
# and the last BIFS is a class definition from that file.
# Since BIFS is not a module, I don't think __all__ will work with it.
from bifs.bifscore import BIFS
from bifs import pset_dialogs
