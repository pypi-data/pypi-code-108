import os
import tempfile
from enum import Enum
from typing import Optional, Union
from shutil import copyfile 

class ResultFileType(Enum):
    BYTE_ARRAY = 0
    FILE_PATH = 1

class ResultFile():
    def __init__(self, result_file_type:ResultFileType, file_name:str, byte_array:Optional[bytes]=None, file_path:Optional[str]=None):
        """Create a new ResultFile() object.

        Keyword arguments:
        result_file_type -- ResultFileType enum element to identify the result file source format (byte array or file path).
        file_name -- (Optional) Filenamed returned for byte array result files by the soap client.
        byte_array -- (Optional) Files bytes returned by the soap client.
        file_path -- (Optional) File path returned by the com client.
        """ 
        self.type = result_file_type

        if self.type == ResultFileType.BYTE_ARRAY:
            self.name = file_name
            self.__bytes__ = byte_array
            self.__path__ = None
        
        elif self.type == ResultFileType.FILE_PATH:
            self.name = os.path.basename(file_path)
            self.__bytes__ = None
            self.__path__ = file_path

        self.extension = os.path.splitext(self.name)[1]


    def size(self) -> int:
        """Return the file size of the ResultFile."""        
        if self.type == ResultFileType.BYTE_ARRAY and self.__bytes__:
            return len(self.__bytes__)
        
        elif self.type == ResultFileType.FILE_PATH and self.__path__:
            return os.path.getsize(self.__path__)
        
        return 0
        

    def store(self, path:Optional[str]=None) -> Union[str, None]:
        """Store the ResultFile to disk and return the storage path.

        Keyword arguments:
        path -- (Optional) String with target path. When omitted, the file will be saved at a temporary directory.
        """

        if self.type == ResultFileType.BYTE_ARRAY and self.__bytes__:
            if path == None:
                path = os.path.join(tempfile.gettempdir(), self.name)
            with open(path, 'wb') as file:
                file.write(self.__bytes__)
                file.close()
            return path

        elif self.type == ResultFileType.FILE_PATH and self.__path__:
            if path == None:
                return self.__path__
            copyfile(self.__path__, path)
            return path


    def bytes(self) -> Union[bytes, None]:
        """Return the ResultFile as bytearray."""

        if self.__bytes__:
            return self.__bytes__

        if self.__path__:
            with open(self.__path__, 'rb') as fp: 
                self.__bytes__ = fp.read()
            return self.__bytes__

        return None