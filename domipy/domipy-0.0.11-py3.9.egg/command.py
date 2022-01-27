"""
Port for Domintell
:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import domipy
from domipy.module_directory import get_point_id

class Command(domipy.Message):
    # pylint: disable-msg=R0904
    """
    Base Domintell message
    """

    def __init__(self, module_type=None, serial_number=None, channel=0, command=None, data=None):
        domipy.Message.__init__(self, module_type, serial_number)
        self._command = command
        self._data = data
        self._channel = channel

    def populate(self, serial_number, data_type, data_string):
        pass

    def command(self):

        module_type = self.moduleType
        serial_number = self.serialNumber
        channel = self._channel
        data_type = self._command
        value = self._data

        point_id = get_point_id(module_type, serial_number, channel)

        if data_type is None:
            data_type = ''

        if len(data_type) < 1:
            data_type = ''

        if channel is None or channel == -1:
            # module without channel
            if value is not None:
                return "{:3}{:>6}{}{}".format(module_type, point_id, data_type, value)
            return "{:3}{:6d}{}".format(module_type, point_id, data_type)
        else:
            # normal multichannel module
            if value is not None:
                return "{:3}{:>8}{}{}".format(module_type, point_id, data_type, value)
            return "{:3}{:>8}{}".format(module_type, point_id, data_type)

    def to_string(self):
        """
        Convert to domintell controll string
        This method can be overridden in subclasses to include more than just generic attributes
        :return: str
        """
        return self.command()

    def get_values(self):
        raise NotImplementedError
