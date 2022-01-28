"""
:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import domipy


class SetAnalogOutputMessage(domipy.Command):

    def __init__(self, module_type, serial_number, channel=0, value=0):
        domipy.Command.__init__(self, module_type, serial_number, channel, "%D", value)

