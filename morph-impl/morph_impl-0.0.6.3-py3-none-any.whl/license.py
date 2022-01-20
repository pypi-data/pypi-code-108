import json
import yaml
import requests
import os
#from dotenv import load_dotenv
import logging

# IMPORT ENVIRONMENT
#load_dotenv()
#DEBUG = os.getenv("DEBUG")
#DEBUG_PATH = os.getenv("DEBUG_PATH")
#DEBUG_FILE = os.getenv("DEBUG_FILE")
#LICENSE_CONFIG = os.getenv("LICENSE_CONFIG")
# SETUP LOGGING
#logger = logging.getLogger('logger')

# Add POC License (Yaml)
def add_license(baseURL,bearerToken, yaml_file):
  url = baseURL+"/api/license"
  headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' +bearerToken}
  configfile = yaml_file
  try: 
    with open(configfile) as f:
      result = yaml.safe_load(f)
   #   logger.info("Loaded config file: "+configfile)
  except Exception as e:
    print("error")
   # logger.error("Exception occurred", exc_info=True)
   # logger.debug(configfile)
   # logger.error("Script was not able to open: "+configfile)
   # logger.error("Please check that the file exists.")
  keys = list(result.keys())
  for license in keys:
    key = result[license]['key']
    payload = json.dumps({
        "license": key
    })
 #   logger.debug("Key: "+key)
 #   logger.debug("URL "+baseURL)
 #   logger.debug("Config File: "+LICENSE_CONFIG)
    requests.request("PUT", url, verify=False, headers=headers, data=payload)
 #   logger.info("License Applied")
  print("License: Complete")