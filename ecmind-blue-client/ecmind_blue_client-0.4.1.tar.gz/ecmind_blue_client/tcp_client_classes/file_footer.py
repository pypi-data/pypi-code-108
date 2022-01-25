from protlib import CStruct, CString

class FileFooter(CStruct):
    seperator1 = CString(default="@", length=1)  # always @
    dummy1 = CString(default="0000000000", length=10)  # always @
    magic = CString(default="@MAERTSSA", length=9)  # always @ASSTREAM