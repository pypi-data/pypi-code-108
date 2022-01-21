from typing import Optional, Union, List, Dict

import quickstats

from quickstats.utils.io import VerbosePrint

class AbstractObject(object):
    
    stdout = quickstats._PRINT_
    
    def __init__(self, verbosity:Optional[Union[int, str]]=None):
        
        if verbosity is None:
            self.stdout = quickstats._PRINT_
        else:
            self.stdout = VerbosePrint(verbosity)
        
            
    def set_verbosity(self, verbosity:Optional[Union[int, str]]):
        """
            Change the verbosity of the current class. This will detach the class's standard output 
            from the centrally-managed standard output.
        """
        self.stdout = VerbosePrint(verbosity)