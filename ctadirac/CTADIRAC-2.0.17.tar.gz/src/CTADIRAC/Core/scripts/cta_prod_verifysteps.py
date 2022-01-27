#!/usr/bin/env python
""" Collection of simple functions to verify each of
    the main Prod3MCJob steps
"""

# generic imports
import os
import glob

# DIRAC imports
import DIRAC
# To do: change import
from DIRAC.Core.Base import Script

Script.setUsageMessage('\n'.join([__doc__.split('\n')[1],
                                  'Usage:',
                                  '  %s stepName' % Script.scriptName,
                                  'Arguments:',
                                  '  stepName: corsika, simtel, merging',
                                  '\ne.g: %s corsika' % Script.scriptName
                                  ]))

Script.parseCommandLine()

def clean_output_file(output_files):
  """ Delete Local Files
  """
  DIRAC.gLogger.notice('Deleting Local Files')
  for afile in output_files:
    DIRAC.gLogger.warn('Remove local File %s' % afile.strip())
    os.remove(afile.strip())

def verify_corsika():
  """ Verify a generic Corsika log file
  """
  DIRAC.gLogger.notice('Verifying Corsika log file')

  # get list of output files
  log_file = glob.glob('Data/corsika/run*/run*.log')
  if len(log_file) != 1:
    DIRAC.gLogger.error('no log file found!')
    DIRAC.exit(-1)

  # check EOR tag
  tag = '=== END OF RUN ==='
  content = open(log_file[0],'rt').read()
  if content.find(tag) < 0:
    DIRAC.gLogger.error('"%s" tag not found!' % tag)
    corsika_files = list(os.popen('find . -iname "*corsika.*z*"'))
    if len(corsika_files) > 0:
      clean_output_file(corsika_files)
    simtel_files = list(os.popen('find . -iname "*simtel.*z*"'))
    if len(simtel_files) > 0:
      clean_output_file(simtel_files)
    log_gz_files = list(os.popen('find . -iname "*log.*z*"'))
    if len(log_gz_files) > 0:
      clean_output_file(log_gz_files)
    log_hist_files = list(os.popen('find . -iname "*log_hist.tar"'))
    if len(log_hist_files) > 0:
      clean_output_file(log_hist_files)
    DIRAC.exit(-1)

def verifySimtel(nbFiles=31, minSize=50.):
  """ Verify a PROD3 simtel step

  Keyword arguments:
  nbFiles -- number of output files expected
  minSize -- minimum file size
  """
  DIRAC.gLogger.notice('Verifying Simtel step')
  # get list of output files
  outputFiles = glob.glob('Data/simtel_tmp/Data/*simtel.*z*')

  # check the number of output files --- could be done by telescope type
  N = len(outputFiles)
  if N != nbFiles:
    DIRAC.gLogger.error('Wrong number of Simtel files : %s instead of %s' %
                        (N, nbFiles))
    clean_output_file(outputFiles)
    DIRAC.exit(-1)

  # check the file size --- could be done by telescope type
  for afile in outputFiles:
    sizekb = os.path.getsize(afile) / 1024.
    if sizekb < minSize:
      DIRAC.gLogger.error('%s\n File size too small : %s < %s kb' % (afile, sizekb, minSize))
      clean_output_file(outputFiles)
      DIRAC.exit(-1)
  DIRAC.gLogger.notice('Good files found:\n%s' % '\n'.join(outputFiles))

def verifyMerging(nbFiles=10, minSize=5000.):
  """ Verify a PROD3 simtel merging step

  Keyword arguments:
  nbFiles -- number of output files expected
  minSize -- minimum file size
  """
  DIRAC.gLogger.notice('Verifying Merging step')

  # get list of output files
  outputFiles = glob.glob('Data/sim_telarray/cta-prod3/0.0deg/Data/*simtel.*z*')

  # check the number of output files --- could be done by telescope type
  N = len(outputFiles)
  if N != nbFiles:
    DIRAC.gLogger.error('Wrong number of Simtel Merged files : %s instead of %s' % (N, nbFiles))
    clean_output_file(outputFiles)
    DIRAC.exit(-1)

  # check the file size --- could be done by telescope type
  for afile in outputFiles:
    sizekb = os.path.getsize(afile) / 1024.
    if sizekb < minSize:
      DIRAC.gLogger.error('%s\n File size too small : %s < %s kb' % (afile, sizekb, minSize))
      clean_output_file(outputFiles)
      DIRAC.exit(-1)
  DIRAC.gLogger.notice('Good files found:\n%s' % '\n'.join(outputFiles))

def verifyAnalysisInputs(minSize=50.):
  """ Verify input files for analysis

  Keyword arguments:
  minSize -- minimum file size
  """
  DIRAC.gLogger.notice('Verifying AnalysisInputs step')

  # get list of output files
  outputFiles = glob.glob('./*simtel.gz')

  # check the file size --- could be done by telescope type
  for afile in outputFiles:
    sizekb = os.path.getsize(afile) / 1024.
    if sizekb < minSize:
      DIRAC.gLogger.warn('%s\n File size too small : %s < %s kb' % (afile, sizekb, minSize))
      DIRAC.gLogger.warn('Remove local File %s' % (afile))
      os.remove(afile)
      outputFiles.remove(afile)  # remove from list of files processed
  DIRAC.gLogger.notice('Good files found:\n%s' % '\n'.join(outputFiles))

def verifyGeneric(nbFiles=1, minSize=50., path='Data/*'):
  """ Verify a PROD3 generic step

  Keyword arguments:
  nbFiles -- number of output files expected
  minSize -- minimum file size
  """
  DIRAC.gLogger.notice('Verifying generic step output')

  # get list of output files
  outputFiles = glob.glob(path)

  # check the number of output files
  N = len(outputFiles)
  if N != nbFiles:
    DIRAC.gLogger.error('Wrong number of output files : %s instead of %s' % (N, nbFiles))
    clean_output_file(outputFiles)
    DIRAC.exit(-1)

  # check the file size
  for afile in outputFiles:
    sizekb = os.path.getsize(afile) / 1024.
    if sizekb < minSize:
      DIRAC.gLogger.error('%s\n File size too small : %s < %s kb' % (afile, sizekb, minSize))
      clean_output_file(outputFiles)
      DIRAC.exit(-1)
  DIRAC.gLogger.notice('Good files found:\n%s' % '\n'.join(outputFiles))

def main():
  """ simple wrapper to put and register all PROD3 files

  Keyword arguments:
  args -- a list of arguments in order []
  """
  # check command line
  args = Script.getPositionalArgs()
  if len(args) < 1:
    DIRAC.gLogger.error('requires at least a step type')
    DIRAC.exit(-1)
  elif len(args) == 1:
    stepType = args[0]
  elif len(args) > 3:
    # now do something
    stepType = args[0]
    nbFiles = int(args[1])
    fileSize = float(args[2])
    if len(args) == 4:
      path = args[3]

  # What shall we verify ?
  if stepType == "corsika":
    verify_corsika()
  elif stepType == "simtel":
    verifySimtel(nbFiles, fileSize)
  elif stepType == "merging":
    verifyMerging(nbFiles, fileSize)
  elif stepType == "analysisinputs":
    verifyAnalysisInputs(fileSize)
  elif stepType == "generic":
    verifyGeneric(nbFiles, fileSize, path)
  else:
    DIRAC.gLogger.error('Do not know how to verify "%s"' % stepType)
    DIRAC.exit(-1)
  DIRAC.exit()

if __name__ == '__main__':
  main()