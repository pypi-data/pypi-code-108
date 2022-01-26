import hashlib as _hashlib
import os as _os
from typing import Callable as _Callable
import SimpleWorkspace as _sw


class FileInfo:
    """
    example case: a/b/test.exe\n
    - filename      = test\n
    - fileExtension = .exe\n
    - tail          = a/b/\n
    - head          = test.exe\n
    - rawPath       = a/b/test.exe\n

    - If no match can be found for any property, they will default to empty string
    """

    tail = ""
    head = ""
    filename = ""
    fileExtension = ""
    rawPath = ""

    def __init__(self, filepath) -> None:
        self.rawPath = filepath
        headTail = _os.path.split(filepath)
        self.tail = headTail[0]
        if self.tail != "":
            self.tail += "/"
        self.head = headTail[1]
        baseName = headTail[1]

        fullFilename = baseName.rsplit(".", 1)
        self.filename = fullFilename[0]
        if len(fullFilename) == 2:
            self.fileExtension = "." + fullFilename[1]


def Hash(filePath: str, hashFunc=_hashlib.sha256()) -> str:
    Read(filePath, lambda x: hashFunc.update(x), readSize=_sw.Conversion.Bytes.MB * 1, getBytes=True)
    return hashFunc.hexdigest()

def Read(filePath: str, callback: _Callable[[str | bytes], None] = None, readSize=-1, readLimit=-1, getBytes=False) -> (str | bytes | None):
    """
    :callback:
        the callback is triggered each time a file is read with the readSize, \n
        callback recieves one parameter as bytes or str depending on getBytes param
    :readSize: amount of bytes to read at each callback, default of -1 reads all at once\n
    :ReadLimit: Max amount of bytes to read, default -1 reads until end of file\n
    :getBytes:
        default True, specifies if the data returned is in string or bytes format\n

    :Returns
        if no callback is used, the filecontent will be returned\n
        otherwise None
    """

    content = b""
    if not getBytes:
        content = ""

    if (readSize == -1 and readLimit >= 0) or (readLimit < readSize and readLimit >= 0):
        readSize = readLimit
    totalRead = 0
    with open(filePath, "rb") as fp:
        while True:
            if readLimit != -1 and totalRead >= readLimit:
                break
            data = fp.read(readSize)
            totalRead += readSize
            if data:
                if not getBytes:
                    data = data.decode()
                if callback == None:
                    content += data
                else:
                    callback(data)
            else:
                break

    if callback is None:
        return content
    return None

def Create(filepath: str, data: bytes | str = None):
    if type(data) is str:
        data = data.encode()
    with open(filepath, "wb") as file:
        if data is not None:
            file.write(data)

def Append(filepath: str, data: bytes | str):
    if type(data) is bytes:
        pass  # all good
    elif type(data) is str:
        data = data.encode()
    else:
        raise Exception("Only bytes or string can be used to append to file")
    with open(filepath, "ab") as file:
        file.write(data)
