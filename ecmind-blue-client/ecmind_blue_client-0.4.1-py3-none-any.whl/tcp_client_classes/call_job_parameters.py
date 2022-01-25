from protlib import CStruct, CString, AUTOSIZED
from .job_parameters import JobParameters

class CallJobParameters(CStruct):
    mode = CString(default="C", length=1)  # always C for call
    method = CString(length=AUTOSIZED)
    internal_parameters = JobParameters.get_type()
    parameters = JobParameters.get_type() 