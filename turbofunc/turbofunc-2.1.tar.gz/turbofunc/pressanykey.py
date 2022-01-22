import sys
try:
    import msvcrt
    windows = True
except ImportError:
    import tty
    import termios
    windows = False
def pressanykey(string="Press any key to continue...", verbose=True, crashOnFailure=False, decodeGetchToUnicode=False, backtrace=False):
    """
    SOURCE: https://raw.githubusercontent.com/TheTechRobo/python-text-calculator/master/FOR%20CLEARING%20THE%20SCREEN%20AND%20PRESS%20ANY%20KEY%20TO%20CONTINUE.md
    Setting verbose to True will cause the function to output a warning message with print() when it fails.
    Setting backtrace to True will raise the backtrace on failure.
    Even if both verbose and backtrace are set to False, the function will end prematurely if it fails.
    Neither of the previous parameters will have any effect if the user is running Windows.
    Setting decodeGetchToUnicode to True will decode the input to Unicode, on Windows. This is the normal behaviour on Linux.
    """
    print(string, end="", flush=True)
    if windows:
       fn = mscvrt.getwch
       if decodeGetchToUnicode: fn = mscvrt.getwch
       return fn()
    else:
       fd = sys.stdin.fileno()
       try:
           settings = termios.tcgetattr(fd)
       except Exception as ename:
           if backtrace:
               raise
           if crashOnFailure:
               raise RuntimeError
           if verbose:
               print("Press any key failed.")
           return False
       try:
           tty.setraw(sys.stdin.fileno())
           return sys.stdin.read(1)
       finally:
           termios.tcsetattr(fd, termios.TCSADRAIN, settings)
