from protlib import CStruct, CString

class JobHeader(CStruct):
    dummy1 = CString(default="L:", length=2)  # always L-
    protocol = CString(default="BIN", length=3)  # BIN or XML
    dummy3 = CString(default="-", length=1)  # always -
    parameter_length = CString(length=10)  # Zero filed byte length of parameters
    version = CString(default="v50", length=3)  # always v50
    compression = CString(default="N", length=1)  # Y or N
    
    def set_parameter_length(self, length):
        self.parameter_length = f"{length:0>10}"

    def get_parameter_length(self):
        return int(self.parameter_length)
