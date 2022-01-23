"""
Nozomi
File Body Class
author: hugh@blinkybeach.com
"""
from nozomi.ancillary.immutable import Immutable


class FileBody:

    def __init__(self, filepath: str) -> None:

        with open(filepath, 'r') as rfile:
            self._body = rfile.read()

        return

    string = Immutable(lambda s: s._body)
