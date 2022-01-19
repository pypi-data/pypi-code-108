from .Spade import Spade, FatalError
from .ItemsFunction import ItemsFunction
from .ApplicationFunction import ApplicationFunction
from .BundlesFunction import BundlesFunction
from .TicketsFunction import TicketsFunction
from .TimingFunction import TimingFunction

import spade_cli
def main():
    """Entry point for the application script"""
    spade_cli.main()
