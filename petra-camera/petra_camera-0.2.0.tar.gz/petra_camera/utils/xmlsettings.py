#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Author:        sebastian.piec@desy.de
# ----------------------------------------------------------------------

"""Parse settings given in xml files
"""

from xml.dom.minidom import parseString


# ----------------------------------------------------------------------
class XmlSettings(object):

    # ----------------------------------------------------------------------
    def __init__(self, fileName):
        self.fileName = fileName

    # ----------------------------------------------------------------------
    def option(self, nodePath, attribute):
        """Retrieve option's value from a config file.
        """
        with open(self.fileName, "r") as inFile:        # read over-and-over??? TODO
            path = nodePath.split("/")

            node = parseString(inFile.read())
            for nodeName in path:
                node = node.getElementsByTagName(nodeName)[0]     # take first node always...

            return node.getAttribute(attribute)

    # ----------------------------------------------------------------------
    def get_nodes(self, nodePath, nodeName):
        """
        """
        with open(self.fileName, "r") as inFile:
            path = nodePath.split("/")[:-1]

            node = parseString(inFile.read())
            for nodeName in path:
                node = node.getElementsByTagName(nodeName)[0]

            return node.getElementsByTagName(nodeName)

    # ----------------------------------------------------------------------
    def node(self, nodePath):
        """
        """
        with open(self.fileName, "r") as f:
            path = nodePath.split("/")

            node = parseString(f.read())
            for nodeName in path[:-1]:
                node = node.getElementsByTagName(nodeName)[0]

            return node.getElementsByTagName(path[-1])[0]           # returns first matching node always...

    # ----------------------------------------------------------------------
    def has_node(self, nodePath):
        try:
            self.node(nodePath)
            return True
        except:
            return False
