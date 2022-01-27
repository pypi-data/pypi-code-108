
class NoStoredConfigError(Exception):
    """
    
    Raised when the program is unable to find a stored config-file or flag-file.
    
    
    """
    def __init__(self, message:str=None, no_print=False, logger=None):
        """
        
        Raised when the program has tried and been unable to find a config file, nor a valid flag file in the given
        locations.
        
        Args:
            message(str): A message to be delivered upon raising of this exception. (*Default* Was unable to find a
                          valid config file, nor was I able to find a valid flag file in this location):
            no_print(bool): Do not do any printing on initialization, let the caller handle it.
        """
        msg = "Was unable to find a valid config file, nor was I able to find a valid flag file in this location"
        if message is not None:
            self.message = msg + f' {message}'
        else:
            self.message = msg
            
        self.msg = self.message
        
        if not no_print:
            print()
