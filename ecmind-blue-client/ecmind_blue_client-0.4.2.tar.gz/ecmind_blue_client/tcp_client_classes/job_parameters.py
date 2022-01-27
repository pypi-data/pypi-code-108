from protlib import CStruct, CInt, CArray
from .job_parameter_description import JobParameterDescription
from .job_parameter_data import JobParameterData

class JobParameters(CStruct):
    length = CInt()
    count = CInt()
    description = CArray(length="count", ctype=JobParameterDescription)
    data = CArray(length="count", ctype=JobParameterData)

    def get(self, name): 
        for data in self.data:
            dName = data.name.decode('ascii')
            if dName == name:
                return data.value
        
        return None