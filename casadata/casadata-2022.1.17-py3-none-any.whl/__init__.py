__name__ = 'casadata'
__all__ = [ 'datapath' ]

import os as _os

datapath=(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'__data__'))
