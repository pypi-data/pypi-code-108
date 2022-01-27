#!/usr/bin/env python
"""
Show the progress of Moving transformations associated to one or more datasets

Warning: Moving transformations are expected to follow the naming convention:
<Move>_<MCCampaign>_<datasetName>
Transformations not following this convention can be inspected directly using the Transformation Web Monitor or the transformation CLI

Usage:
   cta-prod-move-dataset-status <datasetName (may contain wild cards) or ascii file with a list of datasets> <MCCampaign> <target SE>

Example:
   cta-prod-move-dataset-status Paranal_gamma_North_20deg_HB9 PROD3 CC-IN2P3-Tape
"""

__RCSID__ = "$Id$"

import os

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
from CTADIRAC.Core.Utilities.tool_box import read_inputs_from_file
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

def get_list_of_datasets(tag=''):
  fc = FileCatalogClient()
  dataset_tag = '*%s*' % tag
  res = fc.getDatasets(dataset_tag)
  if not res['OK']:
    gLogger.error(res['Message'])
    DIRAC.exit(-1)
  dataset_dict = res['Value']
  dataset_list = list()
  for dataset_name in dataset_dict['Successful'][dataset_tag]:
    dataset_list.append(dataset_name)
  return dataset_list

def get_dataset_info(dataset_name):
  fc = FileCatalogClient()
  res = fc.getDatasets(dataset_name)
  if not res['OK']:
    gLogger.error("Failed to get datasets")
    DIRAC.exit(-1)
  dataset_dict = res['Value']
  res = dataset_dict['Successful'][dataset_name][dataset_name]
  number_of_files = res['NumberOfFiles']
  meta_query = res['MetaQuery']
  total_size = res['TotalSize']
  return (dataset_name, number_of_files, total_size, meta_query)

def get_transformation_info(dataset_name, MCCampaign, targetSE):

  transClient = TransformationClient()

  paramShowNames = [
      "TransformationID",
      "TransformationName",
      "Type",
      "Status",
      "Files_Total",
      "Files_PercentProcessed",
      "Files_Processed",
      "Files_Unused",
      "Jobs_TotalCreated",
      "Jobs_Waiting",
      "Jobs_Running",
      "Jobs_Done",
      "Jobs_Failed",
      "Jobs_Stalled",
  ]

  trans_name = ("Move_%s_%s_%s" % (MCCampaign, targetSE, dataset_name))
  res = transClient.getTransformationParameters(trans_name, 'TransformationID')

  if not res['OK']:
    gLogger.error("Warning: failed to get transformation %s" % (trans_name))
    return "_"

  transID = res['Value']
  res = transClient.getTransformationSummaryWeb({"TransformationID": transID}, [], 0, 1)

  if not res["OK"]:
      DIRAC.gLogger.error(res["Message"])
      DIRAC.exit(-1)

  if res["Value"]["TotalRecords"] > 0:
    paramNames = res["Value"]["ParameterNames"]
    for paramValues in res["Value"]["Records"]:
      paramShowValues = map(lambda pname: paramValues[paramNames.index(pname)], paramShowNames)
      showDict = dict(zip(paramShowNames, paramShowValues))
      files_PercentProcessed = showDict["Files_PercentProcessed"]

  return files_PercentProcessed

#########################################################
@Script()
def main():

  _, argss = Script.parseCommandLine(ignoreErrors=True)

  if len(argss) != 3:
    Script.showHelp()

  if os.path.isfile(argss[0]):
    gLogger.notice('\nReading datasets from input file: %s\n' % argss[0])
    dataset_list = read_inputs_from_file(argss[0])
  else:
    dataset_name = argss[0]
    dataset_list = list()
    if dataset_name.find('*') > 0:
      dataset_list = get_list_of_datasets(dataset_name)
      if len(dataset_list) == 0:
        gLogger.notice("No dataset found")
        DIRAC.exit()
    else:
      dataset_list.append(dataset_name)

  MCCampaign =  argss[1]
  targetSE =  argss[2]

  values = []
  for dataset_name in dataset_list:
    name, n_files, size, mq = get_dataset_info(dataset_name)
    # # convert total size in TB
    size_TB = size / 1e12
    # get transformation info
    files_PercentProcessed = get_transformation_info(dataset_name, MCCampaign, targetSE)
    values.append((name, n_files, float("{:.2f}".format(size_TB)), files_PercentProcessed))

  # print table
  gLogger.notice('\n|_. Name |_. N files |_. Size(TB) |_. Files Processed (%)| ')
  for value in values:
    gLogger.notice("|%s|" % "|".join(map(str,value)))

  DIRAC.exit()

if __name__ == '__main__':
  main()
