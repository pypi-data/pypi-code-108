import abc
from abc import ABC, abstractmethod

from whizbang.data.az_cli_context import AzCliContext
from whizbang.data.az_cli_response import AzCliResponse


class IAzRepository(ABC):
    @abstractmethod
    def _execute(self, command: str):
        """the execute interface"""


class AzRepositoryBase(IAzRepository):
    def __init__(self, az_cli_context: AzCliContext):
        self.__context = az_cli_context

    @property
    @abstractmethod
    def _resource_provider(self) -> str:
        """name of the resource provider api"""

    def _execute(self, command: str, sterilized_command=None, secret_response = False) -> AzCliResponse:
        """This function calls the AZ CLI and returns the results to the caller.  
        
            It's imperative that the caller provide a sterilized command for logging on any sensitive calls.  Similarly, calls returning sensitive data should be marked.
            
            Callers should also consider catching AzCliException, or one of the specific children (see below).
        
            Non-zero exit codes emit an exception:
                - 0 = success, 
                - 1 = request error, -> throws AzCliRequestError
                - 2 = command parsing error, -> throws AzCliCommandParsingError
                - 3 = resource does not exist -> throws AzCliResourceDoesNotExist
                
            By default, the CLI will return execution information that callers can interpret.
        """        
        # We add the same verbose flag.
        if sterilized_command is not None:
            sterilized_command = f'{self._resource_provider} {sterilized_command} --verbose'
            
        return self.__context.execute(f'{self._resource_provider} {command} --verbose', sterilized_command=sterilized_command, secret_response=secret_response)
