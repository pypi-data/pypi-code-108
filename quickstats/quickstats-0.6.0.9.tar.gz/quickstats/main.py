from typing import List, Union, Optional, Dict
import os
import glob

import quickstats

def compile_macros(macros:Optional[Union[str, List[str]]]=None):
    """
    Compile ROOT macros
    
    Arguments:
        macros: (Optional) str or list of str
            If str, it is a string containing comma delimited list of macro names to be compiled.
            If list of str, it is the list of macro names to be compiled.
    """
    if macros is None:
        macros = get_all_macros()
    elif isinstance(macros, str):
        macros = macros.split(',')
    from quickstats.utils.root_utils import compile_macro
    for macro in macros:
        compile_macro(macro)
        
def get_all_macros():
    """
    Get the list of macros names
    
    Note: Only macros ending in .cxx will be considered
    """
    macros_dir = os.path.join(quickstats.macro_path, 'macros')
    macro_paths = glob.glob(os.path.join(macros_dir, "*.cxx"))
    macros = [os.path.os.path.splitext(os.path.basename(path))[0] for path in macro_paths]
    return macros


def set_verbosity(verbosity:Union[str, int]="INFO"):
    quickstats._PRINT_.verbosity = verbosity