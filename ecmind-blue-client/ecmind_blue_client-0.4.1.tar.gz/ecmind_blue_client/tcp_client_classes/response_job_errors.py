from protlib import CStruct, CInt, CArray
from .response_job_error_description import ResponseJobErrorDescription
from .response_job_error_data import ResponseJobErrorData

class ResponseJobErrors(CStruct):
    length = CInt()
    count = CInt()
    dummy = CInt()
    description = CArray(length="count", ctype=ResponseJobErrorDescription.get_type())
    data = CArray(length="count", ctype=ResponseJobErrorData.get_type())