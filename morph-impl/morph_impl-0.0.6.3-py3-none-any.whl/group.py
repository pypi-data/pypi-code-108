import json
import yaml
import requests
import os
import glob
from tqdm import tqdm
import urllib3
from . import morph_log
# Disable Warning for URL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getGroups(baseURL, bearerToken, name):
  """
  # Get Group ID

  ## Summary: 
  If a group ID is required this module will search the api for the ID of a named group.  

  ### Inputs
  - baseURL - the appliance URL 
  - bearerToken - the bearer token for ADMIN_USERNAME and ADMIN_PASSWORD
  - name - name of the group

  associated module: morph_impl.getBearerToken, getGroups_helper
  """
  logger = morph_log.get_logger('getg')
  logger.debug('###########    DEBUG    #############')
  logger.debug('Name: '+name)
  logger.debug('bearerToken: '+bearerToken)
  logger.debug('baseURL: '+baseURL)
  logger.debug('###########    DEBUG    #############')
  try:
    return getGroups_helper(baseURL, name, bearerToken, logger)
  except Exception as e:
    logger.warning(
        name +
        ' Found Null Value for Group Lookup.  Setting Variable to "none" and passing exception'
    )
    return 'none'

def getGroups_helper(baseURL, name, bearerToken, logger):
  url = baseURL+'/api/groups?name='+name
  headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
  result = requests.request("GET", url, verify=False, headers=headers)
  jsonData = result.json()
  groupID = jsonData['groups'][0]['id']
  logger.debug('###########    DEBUG    #############')
  logger.debug('url: '+url)
  logger.debug('groupID: '+ str(groupID))
  logger.debug('baseURL: '+baseURL)
  logger.debug('###########    DEBUG    #############')
  return groupID


def createGroups(baseURL, bearerToken, yaml_file):
  """
  # Create Groups

  ## Summary:
  With at yaml file, list of groups this module will create all the groups in a file.  It will also validate the yaml file meets the expected formatting.

  ### Inputs
  - baseURL - the appliance URL
  - bearerToken - the bearer token for ADMIN_USERNAME and ADMIN_PASSWORD
  - yaml_file - yaml file with list of group names to be added. 

  associated module: morph_impl.getBearerToken, getGroups
  """
  logger = morph_log.get_logger('cg')
  url = baseURL+"/api/groups"
  files = glob.glob(yaml_file)
  for file in tqdm(files, desc="Groups"):
      yaml_file = file
      logger.debug('Current YAML File: '+yaml_file)
      with open(yaml_file) as f:
        try:
          result = yaml.safe_load(f)
        except Exception as e:
            logger.error('Exception: ', e)
      for k, v in result['groups'].items():
        name = result['groups'][k]['name']
        description = result['groups'][k]['description']
        location = result['groups'][k]['location']
        code = result['groups'][k]['code']
        payload = json.dumps({
                                "group":{
                                  "name": name,
                                  "description": description,
                                  "location": location,
                                  "code": code
                                }
                              })
        groupCheck = getGroups(baseURL, bearerToken, name)
        if groupCheck == 'none':
          logger.warning('Group Not Found - Creating: '+name)
          headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + bearerToken}
          response = requests.request("POST", url, verify=False, headers=headers, data=payload)
          jsonData = json.loads(response.text)
          if jsonData["success"] == False:
              logger.error("Failed to add group")
        else:
          logger.info('Group Found - Skipping: '+name) 