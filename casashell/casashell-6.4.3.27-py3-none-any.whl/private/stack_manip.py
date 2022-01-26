import inspect

###
### The stack available when invoking object member functions seems to
### be truncated. It is necessary to find the top frame in __init__(...)
### or the global module execution (i.e. outside of class definition).
###
def find_frame( ):
    frame = inspect.currentframe( )
    while frame is not None:
        if '__casashell_state__' in frame.f_globals:
            return frame.f_globals
        frame = frame.f_back
    return None

def find_global(sym):
    frame = inspect.currentframe( )
    while frame is not None:
        if sym in frame.f_globals:
            return frame.f_globals[sym]
        frame = frame.f_back
    return None

def find_local(sym):
    frame = inspect.currentframe( )
    while frame is not None:
        if sym in frame.f_locals:
            return frame.f_locals[sym]
        frame = frame.f_back
    return None
