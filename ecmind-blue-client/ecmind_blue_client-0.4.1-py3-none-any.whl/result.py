from .result_file import ResultFile
from typing import List, Optional

class Result():
    def __init__(self, values:dict={}, files:List[ResultFile]=[], return_code:int=-1, error_message:Optional[str]='', client_infos:Optional[dict]={}):
        """Create a new Result() object.

        Keyword arguments:
        values -- Dictionary of output parameters.
        files -- List of ResultFile() output file parameters.
        return_code -- Integer representation of the job result.
        error_message -- String containing error responses from the server on None if return_code is 0.
        client_infos -- List of optional data returned by the individual client implementation.
        """
        self.values = values
        self.files = files
        self.return_code = return_code
        self.error_message = error_message
        self.client_infos = client_infos

    def __repr__(self):
        if self.return_code == 0:
            return f'Result (success, {len(self.files)} files): {self.values}'
        else:
            return f'Result (failed, code {self.return_code}): {self.error_message}'