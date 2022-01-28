import json
import domipy


class LoginRequestSaltCommand(domipy.Command):
    """
        send: REQUESTSALT@<username>
    """
    def __init__(self, username):
        domipy.Command.__init__(self, "REQUESTSALT@", "REQUESTSALT@")
        self._username = username

    def command(self): 
        return "REQUESTSALT@" + self._username

    def is_binary(self):
        return True

class LoginRequestSaltMessage(domipy.Message):
    """
    Session opened message
    """

    def __init__(self, moduleType=None, data=None):
        domipy.Message.__init__(self)
       
        self.moduleType = 'REQUESTSALT'
        self.username = data[2].split('=')[1]
        self.nonce = data[3].split('=')[1]
        self.salt = data[4].split("=")[1]
        self._message = data
    
    def populate(self, serialNumber, dataType, dataString):
        pass

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict['username'] = self.username
        json_dict['nounce'] = self.nonce
        json_dict['salt'] = self.salt
        return json.dumps(json_dict)
