#!/usr/bin/env python

__RCSID__ = "$Id$"

# generic imports
from multiprocessing import Pool
import signal
import os

# DIRAC imports
from DIRAC import gLogger
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script

Script.setUsageMessage("""
Bulk get replicas from a list of lfns
Usage:
   cta-prod-get-file [options] <ascii file with lfn list>
""")

Script.parseCommandLine(ignoreErrors=True)
# Import of DIRAC API must comes after parseCommandLine
from DIRAC.Interfaces.API.Dirac import Dirac

TEMPDIR = '.incomplete'

def sigint_handler(signum, frame):
  '''
  Raise KeyboardInterrupt on SIGINT (CTRL + C)
  This should be the default, but apparently Dirac changes it.
  '''
  raise KeyboardInterrupt()

def getfile(lfn):
  dirac = Dirac()
  gLogger.notice('Start downloading file', lfn)
  res = dirac.getFile(lfn, destDir=TEMPDIR)

  if not res['OK']:
    gLogger.error('Error downloading file', lfn)
    return res['Message']

  name = os.path.basename(lfn)
  os.rename(os.path.join('.incomplete', name), name)
  gLogger.notice('Successfully downloaded file', lfn)

@Script()
def main():
  args = Script.getPositionalArgs()
  if len(args) == 1:
    infile = args[0]
  else:
    Script.showHelp()

  # put files currently downloading in a subdirectory
  # to know which files have already finished
  if not os.path.exists(TEMPDIR):
    os.makedirs(TEMPDIR)

  infileList = read_inputs_from_file(infile)
  # see https://stackoverflow.com/a/35134329/3838691
  # ignore sigint before creating the pool,
  # so child processes inherit the setting, we will terminate them
  # if the master process catches sigint
  signal.signal(signal.SIGINT, signal.SIG_IGN)
  p = Pool(10)
  # add the original handler back
  signal.signal(signal.SIGINT, sigint_handler)

  try:
    future = p.map_async(getfile, infileList)

    while not future.ready():
      future.wait(5)
  except (SystemExit, KeyboardInterrupt):
    gLogger.fatal('Received SIGINT, waiting for subprocesses to terminate')
    p.close()
    p.terminate()
  finally:
    p.close()
    p.join()
    if len(os.listdir(TEMPDIR)) == 0:
      os.rmdir(TEMPDIR)

if __name__ == '__main__':
  main()