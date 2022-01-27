__name__ = "scratchlink"
__version__ = "1.0.1"
__developer__ = "Siddhesh Chavan"
__documentation__ = "https://github.com/Sid72020123/scratchlink"
__doc__ = f"""
ScratchLink Python Library:
    Simple Python Library to get the Scratch Data. This library is a simple form of the scratchconnect Python Library.
Made By:
    {__developer__} or @Sid72020123 on Scratch
Documentation:
    {__documentation__}
History:
    11/12/2021(v0.5) - First Started Making This Library.
    12/12/2021(v1.0) - Updated and First Release!
    27/01/2022(v1.0.1) - Updated Comments API
"""

from scratchlink.ScratchLink import ScratchLink
from scratchlink import Exceptions

print(f"{__name__} v{__version__} - {__documentation__}")
