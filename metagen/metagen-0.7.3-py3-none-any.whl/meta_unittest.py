#!/usr/bin/python3

from .metagenerator import MyMetadata


def test1():
    """1 maintainer"""
    metadata = MyMetadata()
    metadata.set_maintainer(["<pythonhead@gentoo.org>"], 
                            ["Rob Cakebread"], 
                            ["Maintainer description."],
                            ["person"])
    return metadata 
    
def test2():
    """2 maintainers, longdesc"""
    metadata = MyMetadata()
    metadata.set_maintainer(["goofy@gentoo.org", "pythonhead@gentoo.org"],
                            ["Goo Fi", "Rob Cakebread"],
                            ["Maintainer one.", "Maintainer two"],
                            ["person", "person"])
    metadata.set_longdescription("This packages does X Y and Z.")
    return metadata 

