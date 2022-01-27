#!/usr/bin/env python
""" Simple data management script for PROD3 MC
    create DFC MetaData structure
    put and register files in DFC
"""

__RCSID__ = "$Id$"

# DIRAC imports
import DIRAC
from DIRAC.Core.Base import Script
 
Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s one two' % Script.scriptName,
                                     'Arguments:',
                                     '  one: one',
                                     '\ne.g: %s ?' % Script.scriptName
                                     ] ) )

Script.parseCommandLine()

# Specific DIRAC imports
from CTADIRAC.Core.Workflow.Modules.ProdDataManager import ProdDataManager

####################################################
def main():
    """ simple wrapper to remove PROD3 local files
    
    Keyword arguments:
    args -- a list of arguments in order []
    """
    args = Script.getPositionalArgs()
    datadir = args[0]
    pattern = args[1]
    catalogs = ['DIRACFileCatalog']
    
    prod3dm = ProdDataManager( catalogs )
    # ## Remove local files
    res = prod3dm.cleanLocalFiles( datadir, pattern )
    if not res['OK']:
      return res

    DIRAC.exit()

####################################################
if __name__ == '__main__':
  main()