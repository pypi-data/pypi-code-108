from .client import Client
from comtypes.client import CreateObject
from comtypes import COMError
import os
from typing import List

from .result import Result
from .result_file import ResultFile, ResultFileType
from .job import Job
from .param import Param
from .const import ParamTypes


class ComClient(Client):
    def __init__(self, hostname:str, port:int, username:str, password:str):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.server = CreateObject('OxSvrSpt.Server')
        self.session = self.server.Login(username, password, hostname, str(port))

    def execute(self, job:Job) -> Result:
        """Send a job to the com server (OxSvrSpt.Server), execute it and return the response.

        Keyword arguments:
        job -- A previously created Job() object.
        """
        native_job = self.session.NewJob(job.name)

        for param in job.params:
            if param.type == ParamTypes.INTEGER:
                native_job.InputParameters.AddNewIntegerParameter(param.name, param.value)
            elif param.type == ParamTypes.BOOLEAN:
                native_job.InputParameters.AddNewBooleanParameter(param.name, param.value)
            elif param.type == ParamTypes.DATE_TIME:
                native_job.InputParameters.AddNewDatetimeParameter(param.name, param.value)
            elif param.type == ParamTypes.DOUBLE:
                native_job.InputParameters.AddNewDoubleParameter(param.name, param.value)
            elif param.type == ParamTypes.STRING:
                native_job.InputParameters.AddNewStringParameter(param.name, param.value)
            elif param.type == ParamTypes.BASE64:
                native_job.InputParameters.AddNewXmlParameter(param.name, param.value)
            elif param.type == ParamTypes.DB:
                raise Exception('parameter type DB is not supported.')
            else:
                raise Exception('Unknown parameter type')

        for f in job.files:
            native_job.InputFileParameters.AddExistFile(f)

        error_message = None
        try:
            native_job.Execute()
            
            result_values = {}
            for op in native_job.OutputParameters:
                result_values[op.Name] = op.XML if op.type == 6 else op.Value

            result_files = []
            for ofp in native_job.OutputFileParameters:
                _, file_name = os.path.split(ofp.FileName)
                rf = ResultFile(ResultFileType.FILE_PATH, file_name=file_name, file_path=ofp.FileName)
                ofp.AutoDelete = False
                result_files.append(rf)
            
            result_return_code = native_job.Errors.ResultCode
            return Result(result_values, result_files, result_return_code, error_message)
        except COMError as ex:
            error_message = str(ex.details)
            return Result(return_code=ex.hresult, error_message=error_message)