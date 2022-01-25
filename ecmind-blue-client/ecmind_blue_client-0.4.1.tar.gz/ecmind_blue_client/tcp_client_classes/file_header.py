from logging import exception
from protlib import CStruct, CString

class FileHeader(CStruct):
    #b'@ASSTREAM@0000147254@docx??????@'
    magic = CString(default="@ASSTREAM@", length=10)  # always @ASSTREAM@
    file_length = CString(length=10)  # Zero filed byte length of file
    seperator1 = CString(default="@", length=1)  # always @
    extension = CString(length=10)  # file extension like docx
    seperator2 = CString(default="@", length=1)  # always @

    def set_file_length(self, length):
        self.file_length = f"{length:0>10}"

    def get_file_length(self):
        return int(self.file_length)

    def get_file_extension(self):
        return str(self.extension, 'ascii').replace('\x11', '')