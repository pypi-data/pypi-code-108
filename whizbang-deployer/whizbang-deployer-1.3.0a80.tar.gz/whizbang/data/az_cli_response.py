from dataclasses import dataclass
from typing import Any

@dataclass
class AzCliResponse:
    """Class for returning invocation details for external programs (cli's)."""
    
    command: str
    """The original command invoked.  This command should be sterilized of any secret information."""
    
    exit_code: int
    """The exit code of the child process."""
    
    results: Any
    """A dictionary which contains the results returned by the CLI.  (or a string if tsv mode is used)
    
        See: https://github.com/MarkWarneke/Az.Cli
    """
    
    secret_response: bool
    """If this command returns secret information, this flag should be set and any information about the results should not be logged."""
    
    logs: str
    """The logs returned by the CLI."""
    
    def __repr__(self) -> str:
        """Returns a string representation of the class for debugging and logging.  Python calls this for str conversion as well.
        
        This implementation removes access to results if they are marked secret.  Callers are responsible for sterilizing secret information in the command attribute.
        """
        
        if self.exit_code==0:
            success = 'Succeeded'
        else:
            success = 'Failed'
            
        results = self.results if not self.secret_response else '**Removed -> secret_response=True**'
            
        return f'AzCliResponse {success}: command({self.command}), exit_code({self.exit_code}), results({results}), logs({self.logs})'
            
            
        
