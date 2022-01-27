
from .Rkd import RkdClient
import json
from cryptography.fernet import Fernet


class Portal:
    credentials:dict=None
    encdata = "gAAAAABh78iBmoBrAma1-1tP9eBXvscJ2l-DQia_5tFHMAXK6edHA72S9MUzkKjgCOtdTnzrm-5vNufxryPlhurvSztpk-BB_2NldStNpn75oJMk23ZGQ83sUfEMy2LZWKQCxrKzDQErT_sqtqGNpXQALhiy6Rg0jezJfjg9QSVxtVYqC6x3c9NxxE-MDgGErGGyn0iW2qwxjiVUFoPaKKMHC__T84qvYcw3gN9ZkYodOAO7OrxdXds="
    
    
    def set_credentials_from_secret(self,secret:str)->None:
        """
        args:
            secret: secret key
        """
        fernet = Fernet(bytes(secret, "utf-8"))
        try:
            decmessage = fernet.decrypt(bytes(self.encdata, "utf-8")).decode()
        except Exception as e:
            raise Exception("Invalid secret")
        self.credentials = json.loads(decmessage)
    
    def set_credentials_from_json(self,path:str)->None:
        """
        args:
            path: path to json file
        """
        with open(path) as f:
            self.credentials = json.load(f)
            f.close()
        
    
    def __creds_exist(self):
        if not self.credentials:
            raise Exception("Credentials not set")
    
    def get_rkd_client(self) -> RkdClient:
        self.__creds_exist()
        return RkdClient(self.credentials["rkd"]["ApplicationID"],self.credentials["rkd"]["Username"],self.credentials["rkd"]["Password"])