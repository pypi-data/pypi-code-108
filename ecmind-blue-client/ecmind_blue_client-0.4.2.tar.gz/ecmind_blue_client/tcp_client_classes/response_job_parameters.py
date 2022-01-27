from protlib import CStruct, CString
from .job_parameters import JobParameters
from .response_job_errors import ResponseJobErrors

class ResponseJobParameters(CStruct):
    mode = CString(default="R", length=1)  # always R for response
    internal_parameters = JobParameters.get_type()
    parameters = JobParameters.get_type()
    errors = ResponseJobErrors.get_type()