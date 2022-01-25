from typing import List
from az.cli import az
import logging

from whizbang.data.az_cli_response import AzCliResponse
from whizbang.domain.exceptions import AzCliCommandParsingError, AzCliRequestError, AzCliResourceDoesNotExist

_log = logging.getLogger(__name__) 

class AzCliContext:

    def execute(self, command, sterilized_command=None, secret_response=False) -> AzCliResponse:
        """This function calls the AZ CLI and returns the results to the caller.  
        
            It's imperative that the caller provide a sterilized command for logging on any sensitive calls.  Similarly, calls returning sensitive data should be marked using secret_response=True.
            
            Callers should also consider catching AzCliException, or one of the specific children (see below).
        
            Non-zero exit codes emit an exception:
                - 0 = success, 
                - 1 = request error, -> throws AzCliRequestError
                - 2 = command parsing error, -> throws AzCliCommandParsingError
                - 3 = resource does not exist -> throws AzCliResourceDoesNotExist
                
            By default, the CLI will return execution information that callers can interpret.
        """        
        # Execute the CLI command
        exit_code: int
        result_dict: dict
        logs: str
        exit_code, result_dict, logs = az(command)
        
        # Create an object to capture the results so we can return it to the caller
        response = AzCliResponse(sterilized_command or command, exit_code=exit_code, results=result_dict, secret_response=secret_response, logs=logs)
               
        # If the exit code is non-zero, raise an exception
        if exit_code != 0:
            error_string = response.__repr__()
            _log.debug(error_string) # this is a debug message, since it may be caught.
            
            if exit_code == 1:
                raise AzCliRequestError(error_string)
            if exit_code == 2:
                raise AzCliCommandParsingError(error_string)
            if exit_code == 3:
                raise AzCliResourceDoesNotExist(error_string)
        
        # Log when we have a zero exit code, but logs are present.
        if response.logs:
            _log.warning(f"Command executed with success exit code, but logs are present: '{response}'")
        
        return response
