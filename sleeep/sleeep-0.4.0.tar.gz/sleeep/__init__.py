"""
sleeep is a better sleep

LICENSE
   MIT (https://mit-license.org/)

COPYRIGHT
   © 2022 Steffen Brinkmann <s-b@mailbox.org>
"""

__author__ = "Steffen Brinkmann"
__version__ = "0.4.0"
__license__ = "MIT"

from .lolcat import LolCat  # noqa: F401
from .term_tools import raw, nonblocking  # noqa: F401
from .bar_tools import bar, styles  # noqa: F401
from .sleeep_main import run, check_term  # noqa: F401
