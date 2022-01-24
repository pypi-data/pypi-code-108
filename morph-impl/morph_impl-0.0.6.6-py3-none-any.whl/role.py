import json
import yaml
import requests
import os
from os import path
import glob
import time
from tqdm import tqdm
from . import morph_log
from . import group
from .classes import(MorphConfig)

def roleGroupCustom(strRoleID):
  logger = morph_log.get_logger('rogpcus')
  morphApi= MorphConfig()
  header = morphApi.header_appJson()
  createRoleApi = morphApi.createRole()
  updateRolePermission = morphApi.updateRolePermission()
  url = createRoleApi+'/'+strRoleID+updateRolePermission
  #headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
  payload = json.dumps({"permissionCode": "ComputeSite", "access": "custom"})
  permissionsResult = requests.request("PUT", url, verify=False, headers=header, data=payload)
  jsonData = json.loads(permissionsResult.text)
  if jsonData["success"] == False:
    logger.error("Role: "+strRoleID)
    logger.error("Tried to update the role but it failed")
    logger.error("Ensure the role exists")
  else:
    logger.debug("Role has been updated to Custom")
    logger.debug("Role: "+strRoleID)
    logger.debug("Role Updated: "+str(permissionsResult.text))

def genericRoleCreate_getRoleID_helper(authority):
  logger = morph_log.get_logger('genrcreate_id_help')
  morphApi= MorphConfig()
  header = morphApi.header_appJson()
  searchRolePhrase = morphApi.searchRolePhrase()
  url = searchRolePhrase+authority
  #headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
  roleResult = requests.request("GET", url, verify=False, headers=header )
  roleID = roleResult.json() #json.loads(roleResult.text)
  role = roleID['roles'][0]['id']
  logger.debug("Get Role ID")
  logger.debug("Role Name: "+authority)
  logger.debug("Role ID: "+str(role))
  logger.debug("URL: "+url)
  logger.debug("Role Result: "+str(roleResult.text))
  return str(role)

def genericRoleCreate_updateRole_feature_helper(strRoleID, result):
  logger = morph_log.get_logger('genrcreate_feat_help')
  morphApi= MorphConfig()
  header = morphApi.header_appJson()
  createRoleApi = morphApi.createRole()
  updateRolePermission = morphApi.updateRolePermission()
  url = createRoleApi+'/'+strRoleID+updateRolePermission
  for k, v in tqdm(result['roleprivs'].items(), desc="Updating Permissions"):
    logger.debug(result['roleprivs'][k]['name'])
    logger.debug(result['roleprivs'][k]['code'])
    logger.debug(result['roleprivs'][k]['access'])
    access = result['roleprivs'][k]['access']
    code = result['roleprivs'][k]['code']
    payload = json.dumps({
      "permissionCode": code,
      "access": access
    })
    #headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
    updateRole = requests.request("PUT", url, verify=False, headers=header, data=payload)
    jsonData = json.loads(updateRole.text)
    if jsonData["success"] == False:
      logger.debug("Feature Access: "+result['roleprivs'][k]['name'])
      logger.debug("Access: "+result['roleprivs'][k]['access'])
      logger.debug("Code :"+result['roleprivs'][k]['code'])
      logger.debug("Result of updating the role: "+str(updateRole.text)+"\n")

def genroleCreate_ifFail_helper(logger, authority, jsonData):
  logger.warning('---- Warning ----')
  logger.warning('Role Name: '+authority)
  logger.warning("Result of creating the role: "+jsonData["errors"]["authority"])
  logger.warning('Ensure the name is unique.')
  logger.debug('Raw: '+str(jsonData))
  logger.warning('---- Warning ----')

def instanceAccess(strRoleID):
  ###### FUTURE FOR MORE ####### 
  logger = morph_log.get_logger('inacc')
  morphApi= MorphConfig()
  header = morphApi.header_appJson()
  createRoleApi = morphApi.createRole()
  updateRolePermission = morphApi.updateRolePermission()
  url = createRoleApi+'/'+strRoleID+updateRolePermission
  #headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
  #url = baseURL+'/api/roles/'+strRoleID+'/update-permission'
  payload=json.dumps({"permissionCode": "InstanceType", "access": "full"})
  instanceAccessResult = requests.request("PUT", url, verify=False, headers=header,data=payload)
  jsonData = json.loads(instanceAccessResult.text)
  if jsonData["success"] == False:
    logger.error("Role: "+strRoleID)
    logger.error("Tried to update the role but it failed")
    logger.error("Ensure the role exists")
  else:
    logger.info("Role Instance Access Updated")
    logger.info("Role: "+strRoleID)
    logger.info("Role Updated: "+str(instanceAccessResult.text))

def blueprintAccess(strRoleID):
  logger = morph_log.get_logger('bpacc')
  ###### FUTURE FOR MORE ####### 
  morphApi= MorphConfig()
  header = morphApi.header_appJson()
  createRoleApi = morphApi.createRole()
  updateRolePermission = morphApi.updateRolePermission()
  url = createRoleApi+'/'+strRoleID+updateRolePermission
  #headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
  #url = baseURL+'/api/roles/'+strRoleID+'/update-permission'
  payload=json.dumps({"permissionCode": "AppTemplate", "access": "full"})
  blueprintAccessResult = requests.request("PUT", url, verify=False, headers=header,data=payload)
  jsonData = json.loads(blueprintAccessResult.text)
  if jsonData["success"] == False:
    logger.error("Role: "+strRoleID)
    logger.error("Tried to update the role but it failed")
    logger.error("Ensure the role exists")
  else:
    logger.info("Role Blueprint Access Updated")
    logger.info("Role: "+strRoleID)
    logger.info("Role Updated: "+str(blueprintAccessResult.text))

def personaAccess(baseURL, strRoleID):
  logger = morph_log.get_logger('peracc')
  ###### FUTURE FOR MORE ####### 
  header = morphApi.header_appJson()
  #headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
  url = baseURL+"/api/roles/"+strRoleID+"/update-persona"
  #standard catalog
  payload=json.dumps({"personaCode": "standard", "access": "full"})
  personaAccessResult = requests.request("PUT", url, verify=False, headers=header,data=payload)
  jsonData = json.loads(personaAccessResult.text)
  if jsonData["success"] == False:
    logger.error("Role: "+strRoleID)
    logger.error("Tried to update the role but it failed")
    logger.error("Ensure the role exists")
  else:
    logger.info("Role Standard Persona Access Updated")
    logger.info("Role: "+strRoleID)
    logger.info("Role Updated: "+str(personaAccessResult.text))

  # service catalog
  payload=json.dumps({"personaCode": "serviceCatalog", "access": "full"})
  personaAccessSCResult = requests.request("PUT", url, verify=False, headers=header,data=payload)
  jsonData = json.loads(personaAccessSCResult.text)
  if jsonData["success"] == False:
    logger.error("Role: "+strRoleID)
    logger.error("Tried to update the role but it failed")
    logger.error("Ensure the role exists")
  else:
    logger.info("Role Service Catalog Persona Access Updated")
    logger.info("Role: "+strRoleID)
    logger.info("Role Updated: "+str(personaAccessSCResult.text))

def groupAccess(result, strRoleID):
  # Grab all files in a folder
  logger = morph_log.get_logger('grpacc')
  morphApi= MorphConfig()
  header = morphApi.header_appJson()
  createRoleApi = morphApi.createRole()
  updateGroupRolePerm = morphApi.updateGroupRolePerm()
  url = createRoleApi+'/'+strRoleID+updateGroupRolePerm
  #headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
  for k, v in tqdm(result['groups'].items(), desc="Adding Groups to Roles"):
    logger.debug(result['groups'][k]['name'])
    logger.debug(result['groups'][k]['access'])
    name = result['groups'][k]['name']
    access = result['groups'][k]['access']
    try:
      # Get Group ID   
      groupID = str(group.getGroups(name))
      #urlGroup = baseURL+'/api/roles/'+strRoleID+'/update-group'
      payloadGroup = json.dumps({"groupId": groupID, "access": access })
      groupPermissionsUpdated = requests.request("PUT", url, verify=False, headers=header, data=payloadGroup)
      jsonData = json.loads(groupPermissionsUpdated.text)
      if jsonData["success"] == False:
        logger.error("Role: "+strRoleID)
        logger.error("Tried to update the role but it failed")
        logger.error("Ensure the role exists")
      else:
        logger.debug("Updating Roles with the proper Groups :"+groupID)
        logger.debug("Role: "+strRoleID)
        logger.debug("Role Updated with Group Name: "+name+' Raw: '+str(groupPermissionsUpdated.text))
    except Exception as e:
      logger.error('Exception occurred', e)

def genericRoleCreate(yaml_file):
  logger = morph_log.get_logger('genrcreate')
   # Setup Class Usage for URL
  morphApi= MorphConfig()
  header = morphApi.header_appJson()
  url = morphApi.createRole()
  files = glob.glob(yaml_file)
  for file in files:
    #yaml_file = file
    logger.info('Current file: '+file)
    with open(file) as f:
      try:
        result=yaml.safe_load(f)
      except yaml.YAMLError as exc:
        logger.error(exc)
        logger.error("Was unable to load the yaml file.")
    authority = result['info']['rolename']
    desc = result['info']['desc']
    roletype = result['info']['roletype']
    payload= json.dumps({"role":{"authority": authority, "description": desc, "roletype": roletype}})
    #headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
    roleResult = requests.request("POST", url, verify=False, headers=header, data=payload)
    logger.debug("")
    logger.debug("Role Result: "+roleResult.text)
    logger.debug("")
    logger.debug("URL "+url)
    jsonData = roleResult.json()
    if jsonData["success"] == False:
      if jsonData["errors"]["authority"] == 'must be unique':
        genroleCreate_ifFail_helper(logger, authority, jsonData)
    else:
      logger.info("Created Role: "+authority)
      logger.info("Role Result: "+str(roleResult.text))   

    # Generic Role Updating. 
    strRoleID = genericRoleCreate_getRoleID_helper(authority)
    genericRoleCreate_updateRole_feature_helper(strRoleID, result)
    roleGroupCustom(strRoleID)
    # Persona Access is for future features
    #personaAccess(baseURL, bearerToken, strRoleID)

    # Blueprint access is for future features
    #blueprintAccess(baseURL, bearerToken, strRoleID)

    # Instance Access is for future features
    #instanceAccess(baseURL, bearerToken, strRoleID)
    logger.debug('Updated Roles with corret feature access: '+authority)
    groupAccess(result, strRoleID)