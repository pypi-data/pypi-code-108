from typing import Any
from cryptography.fernet import Fernet
from PSAPP.Logging.loggingModule import Logging

class DataEncryption:

    def __init__(self, storeNew: bool = True, mainLogger: Logging = None) -> None:
        # self.__mainLogger = mainLogger
        self.__encryptionKey: str = ''
        self.__keyEncryption = 'el1Epnhkrn0uVzscO-tfwf_Y5zs_2O_xX-41HxRDh_g='.encode()
        self.__encryptionKey: str = None
        self.__fernetObjOne: Fernet = Fernet(self.__keyEncryption)
        if (storeNew):
            self.__storeEncryptionKey()

    def __storeEncryptionKey(self):
        with open("key.key", 'wb') as file:
            self.__encryptionKey = Fernet.generate_key()
            file.write(self.__fernetObjOne.encrypt(self.__encryptionKey))

    def __readEncryptionKey(self):
        with open("key.key", 'rb') as file:
            tempKey = file.readline()
            self.__encryptionKey = None
            self.__encryptionKey = self.__fernetObjOne.decrypt(tempKey)

    def encryptData(self, data: Any) -> bytes:
        self.__readEncryptionKey()
        fernetObjTwo = Fernet(self.__encryptionKey)
        encryptedData = fernetObjTwo.encrypt(data.encode())
        return encryptedData
    
    def decryptData(self, data: Any) -> Any:
        self.__readEncryptionKey()
        fernetObjTwo = Fernet(self.__encryptionKey)
        if (type(data) is str):
            data = data.encode()
        decryptedData = fernetObjTwo.decrypt(data)
        return decryptedData