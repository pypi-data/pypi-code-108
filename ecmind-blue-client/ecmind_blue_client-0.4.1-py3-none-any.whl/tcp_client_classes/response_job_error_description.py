from protlib import CStruct, CInt, CArray

class ResponseJobErrorDescription(CStruct):
    message_length = CInt()
    source_code = CInt()
    source_name_length = CInt()
    error_code = CInt()
    info_elements_length =CInt()
    info_elements = CArray(length="info_elements_length", ctype=CInt)