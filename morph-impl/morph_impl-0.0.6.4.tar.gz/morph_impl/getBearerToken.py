import json
import requests
import os
import urllib
from . import morph_log

def bearerToken(baseURL, ADMIN_USERNAME, ADMIN_PASSWORD):
  #ADMIN_USERNAME = urllib.parse.quote(ADMIN_USERNAME)
  logger = morph_log.get_logger('getg')
  url = baseURL+"/oauth/token?grant_type=password&scope=write&client_id=morph-api"
  payload={'username': ADMIN_USERNAME,'password': ADMIN_PASSWORD}
  result = requests.request("POST", url, verify=False, data=payload)
  jsonDump = json.loads(result.text)
  #logger.debug(jsonDump["access_token"])
  return jsonDump["access_token"]  