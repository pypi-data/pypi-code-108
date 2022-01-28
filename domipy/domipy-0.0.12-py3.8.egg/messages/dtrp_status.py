"""
DTRP module status
Output card for the control of 1 to 4 trip switches.

:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import json
import domipy
from domipy.messages import GenericDOStatusMessage

TRP_COMMAND_CODE = "TRP"

class DTRPStatusMessage(GenericDOStatusMessage):
    """
    DTRP module status
    """
    def __init__(self, address=None):
        GenericDOStatusMessage.__init__(self, 4)
        self.moduleType = TRP_COMMAND_CODE

domipy.register_command(TRP_COMMAND_CODE, DTRPStatusMessage)
