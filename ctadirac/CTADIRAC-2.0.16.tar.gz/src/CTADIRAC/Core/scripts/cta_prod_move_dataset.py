#!/usr/bin/env python
'''
Move a dataset distributed on on number of production SEs:
'DESY-ZN-Disk', 'LPNHE-Disk', 'CNAF-Disk', 'CYF-STORM-Disk','LAPP-Disk', 'CEA-Disk', 'CC-IN2P3-Disk', 'LANCASTER-Disk', 'POLGRID-Disk'
to a given destination SE, e.g. CC-IN2P3-Tape

Usage:
cta-prod-move-dataset <dataset name or ascii file with a list of datasets> <dest SE>

Optional arguments:
<group size>: size of the transformation (default=1)
<extra_tag>: extra tag to be appended to the name of the transformation

Example:
Prod4_Paranal_gamma_North_20deg_SSTOnly_MC0 CC-IN2P3-Tape 100

Warning:
If the <extra_tag> option is used the transformations will not be found by the cta-prod-move-status command and should be monitored using
the transformation CLI or the Transformation Web Monitor
'''

__RCSID__ = "$Id$"

import os

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from DIRAC.TransformationSystem.Utilities.ReplicationTransformation import createDataTransformation
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file

def get_dataset_info(dataset_name):
  """ Return essential dataset information
      Name, number of files, total size and meta query
  """
  fc = FileCatalogClient()
  res = fc.getDatasets(dataset_name)
  if not res['OK']:
    gLogger.error(res['Message'])
    DIRAC.exit(-1)
  dataset_dict = res['Value']
  res = dataset_dict['Successful'][dataset_name][dataset_name]
  number_of_files = res['NumberOfFiles']
  meta_query = res['MetaQuery']
  total_size = res['TotalSize']
  return (dataset_name, number_of_files, total_size, meta_query)

@Script()
def main():
  dataset_list = []
  Script.parseCommandLine(ignoreErrors=True)
  argss = Script.getPositionalArgs()
  if len(argss) < 2:
    Script.showHelp()
  if os.path.isfile(argss[0]):
    gLogger.notice('Reading datasets from input file:', argss[0])
    dataset_list = read_inputs_from_file(argss[0])
  else:
    dataset_list.append(argss[0])

  dest_se = argss[1]
  group_size = 1
  extra_tag = ""

  if len(argss) >= 3:
    group_size = argss[2]
  if len(argss) == 4:
    extra_tag = argss[3]

  # Check input data set information
  for dataset_name in dataset_list:
    name, n_files, size, meta_query = get_dataset_info(dataset_name)
    gLogger.notice('Found dataset %s with %d files.' % (name, n_files))
    gLogger.debug(meta_query)
    # choose a metaKey
    # To do: avoid hard coded metakey
    if 'MCCampaign' in meta_query:
      meta_key = 'MCCampaign'
      meta_value = meta_query['MCCampaign']
    else:
       gLogger.error('Error: MCCampaign metadata not defined')
       DIRAC.exit(-1)

    tag = dataset_name
    if extra_tag:
      tag = tag + '_' + extra_tag

    do_it = True
    # To do: replace hard coded SE with SE read from CS
    source_se = ['DESY-ZN-Disk', 'LPNHE-Disk', 'CNAF-Disk', 'CYF-STORM-Disk',
               'LAPP-Disk', 'CEA-Disk', 'CC-IN2P3-Disk', 'POLGRID-Disk', 'LANCASTER-Disk']

    # create Transformation
    res = createDataTransformation(flavour='Moving',
                                   targetSE=dest_se,
                                   sourceSE=source_se,
                                   metaKey=meta_key,
                                   metaValue=meta_value,
                                   extraData=meta_query,
                                   extraname=tag,
                                   groupSize=int(group_size),
                                   plugin='Broadcast',
                                   tGroup=None,
                                   tBody=None,
                                   enable=do_it,
                                   )
    if not res['OK']:
      gLogger.error(res["Message"])
      DIRAC.exit(-1)

  DIRAC.exit()

#########################################################
if __name__ == '__main__':
  main()
