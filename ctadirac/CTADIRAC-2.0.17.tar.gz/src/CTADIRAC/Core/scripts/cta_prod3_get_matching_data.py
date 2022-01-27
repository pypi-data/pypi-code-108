#!/usr/bin/env python
""" Collection of functions to download data files
matching a given pattern / query.

         cta-prod3-get-matching-data.py JB, LA 2016
"""

__RCSID__ = "$Id$"

# generic imports
import os
import six

# DIRAC import Script
import DIRAC
from DIRAC.Core.Base import Script

Script.setUsageMessage('\n'.join([__doc__.split('\n')[1],
                                  'Usage:',
                                  '  %s funcName' % Script.scriptName,
                                  'Arguments:',
                                  '  stepName: sub5, sub2sub5, HB9SCT, HB9merged',
                                  '\ne.g: %s sub5' % Script.scriptName
                                  ]))

Script.parseCommandLine()

# Other DIRAC imports
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient


def downloadFile(lfn):
  """ Download a file using DMS
  Keyword arguments:
  lfn -- a logical file name
  """
  # First check if the file exists
  fc = FileCatalogClient()
  res = fc.exists(lfn)
  if not res['OK']:
    DIRAC.gLogger.error(res['Message'])

  if res['Value']['Successful'][lfn]:
    DIRAC.gLogger.info('Downloading ', lfn)
    dm = DataManager()
    res = dm.getFile(lfn)
    if not res['OK']:
      DIRAC.gLogger.error(res['Message'])

    if lfn not in res['Value']['Successful']:
      DIRAC.gLogger.error('Could not download %s' % lfn)
      return DIRAC.S_ERROR()
  else:
    return DIRAC.S_ERROR('File not found in Catalog')

  return DIRAC.S_OK()


def getSub5():
  """ Download subarray-5 files corresponding to a list of subarray-2 files

  Keyword arguments:
  none -- none
  """
  DIRAC.gLogger.info('Get Subarray-5 files')
  # get JDL
  dirac = Dirac()
  resJDL = dirac.getJobJDL(os.environ['JOBID'])

  # get list of output files
  idata = resJDL['Value']['InputData']

  # dowload files
  for sub2 in idata:
    DIRAC.gLogger.debug("Input %s " % sub2)
    sub5 = sub2.strip('\n').replace('subarray-2-nosct', 'subarray-5-nosct')
    downloadFile(sub5)

  return DIRAC.S_OK()


def getSub2Sub5():
  """ Download subarray-2 and 5 files corresponding to a list of subarray-1 files

  Keyword arguments:
  none -- none
  """
  DIRAC.gLogger.info('Get Subarray-2 and 5 files')
  # get JDL
  dirac = Dirac()
  resJDL = dirac.getJobJDL(os.environ['JOBID'])

  # get list of output files
  idata = resJDL['Value']['InputData']

  # dowload files
  for sub1 in idata:
    DIRAC.gLogger.debug("Input %s " % sub1)
    sub2 = sub1.strip('\n').replace('subarray-1-nosct', 'subarray-2-nosct')
    downloadFile(sub2)
    sub5 = sub1.strip('\n').replace('subarray-1-nosct', 'subarray-5-nosct')
    downloadFile(sub5)

  return DIRAC.S_OK()


def getHB9SCT():
  """ Download SCT files corresponding to a list of HB9 merged files

  Keyword arguments:
  none -- none
  """
  DIRAC.gLogger.info('Get HB9-SCT files')
  # get JDL
  dirac = Dirac()
  resJDL = dirac.getJobJDL(os.environ['JOBID'])
  # get list of output files
  idata = resJDL['Value']['InputData']

  # dowload files
  for merged in idata:
    DIRAC.gLogger.debug("Input %s " % merged)
    sct = merged.strip('\n').replace('merged', 'SCT').replace('cta-prod3', 'cta-prod3-sct')
    res = downloadFile(sct)

  return res


def getHB9merged():
  """ Download HB9 merged files corresponding to a list of SCT files

  Keyword arguments:
  none -- none
  """
  DIRAC.gLogger.info('Get HB9 files')
  # get JDL
  dirac = Dirac()
  resJDL = dirac.getJobJDL(os.environ['JOBID'])

  # get list of output files
  idata = resJDL['Value']['InputData']
  if isinstance(idata, six.string_types):
    idata = []
    if 'LFN' in resJDL['Value']['InputData']:
      idata.append(resJDL['Value']['InputData'].split('LFN:')[1])
    else:
      idata.append(resJDL['Value']['InputData'])
  else:
    idata = resJDL['Value']['InputData']

  # dowload files
  count = 0
  for sct in idata:
    DIRAC.gLogger.notice("Input %s " % sct)
    merged = sct.strip('\n').replace('SCT', 'merged').replace('cta-prod3-sct', 'cta-prod3')
    res = downloadFile(merged)
    if res['OK']:
      count = +1

  if count == 0:
    return DIRAC.S_ERROR("No files downloaded")

  return DIRAC.S_OK()

# Main
def main():
  """ simple wrapper to download data files matching a pattern

  Keyword arguments:
  args -- a list of arguments in order []
  """
  # check command line
  args = Script.getPositionalArgs()
  if len(args) != 1:
    res = DIRAC.S_ERROR()
    res['Message'] = 'Just give the function you wish to use: sub5, sub2sub5, HB9SCT, HB9merged'
    return res

  # now do something
  funcName = args[0]

  # What shall we verify ?
  if funcName == "sub5":
    res = getSub5()
  elif funcName == "sub2sub5":
    res = getSub2Sub5()
  elif funcName == "HB9SCT":
    res = getHB9SCT()
  elif funcName == "HB9merged":
    res = getHB9merged()
  else:
    res = DIRAC.S_ERROR()
    res['Message'] = 'Function "%s" not known' % funcName

  if not res['OK']:
    DIRAC.gLogger.error ( res['Message'] )
    DIRAC.exit(-1)

  DIRAC.exit()


####################################################
if __name__ == '__main__':
  main()