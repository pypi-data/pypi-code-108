from protlib import CStruct, CString, AUTOSIZED

class ResponseJobErrorData(CStruct):
    source_name = CString(length=AUTOSIZED)
    error_message = CString(length=AUTOSIZED)