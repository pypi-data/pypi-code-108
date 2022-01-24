"""Provides interoperability between Maptek Vulcan and the OMF (Open Mining
Format)


Examples
--------
Convert all supported OMF types to an equivalent Vulcan files and types.

>>> from vulcanomf import omf_to_vulcan_project
>>> omf_to_vulcan_project('example.omf', 'vulcan_projects/example')

"""
###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

from .importer import omf_to_vulcan_project
