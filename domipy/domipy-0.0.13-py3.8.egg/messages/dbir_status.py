"""
BIR module status
Output card to control 8 250V/8A two-pole relays.

:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import json
import domipy
from domipy.messages import GenericDOStatusMessage

BIR_COMMAND_CODE = "BIR"

class DBIRStatusMessage(GenericDOStatusMessage):
    """
    DBIR module status
    """

    def __init__(self, address=None):
        GenericDOStatusMessage.__init__(self, 8)
        self.moduleType = BIR_COMMAND_CODE

domipy.register_command(BIR_COMMAND_CODE, DBIRStatusMessage)
