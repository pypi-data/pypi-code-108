"""
Module Info Message
:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import json
import domipy

class InfoMessage(domipy.Message):
    """
    Generic info message
    """

    def __init__(self, moduleType=None, data=None):

        domipy.Message.__init__(self)

        self._message = ''
        self.moduleType = 'INFO'
        self._message = data
    
    def populate(self, serialNumber, dataType, dataString):
        pass

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict['info_message'] = self._message
        return json.dumps(json_dict)

domipy.register_command("INF", InfoMessage)
domipy.register_command("!! ", InfoMessage)
domipy.register_command("APP", InfoMessage)