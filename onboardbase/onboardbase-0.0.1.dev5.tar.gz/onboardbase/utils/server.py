import requests
from json import loads
from ..config import ConfigManager
from ..utils.system import createFallbackSecret, getFallbackSecret, pruneDictionary, getLocalSecret
from ..utils.crypto import aesDecryptSecret
from ..utils.url import url

def fetchSecrets(project, environment):
  configManager = ConfigManager()
  config = configManager.getConfig()
  query = {'query': 'query {generalPublicProjects(filterOptions: {title: "%s", disableCustomSelect: true}){list {id title publicEnvironments(filterOptions: {title: "%s"}){list {id key title}}}}}'%(project, environment)}
  try:
    response = requests.post(url, json=query, headers={'KEY': config["api_key"]})
    if 'errors' in response.json() and response.json()[0]['message'] == 'Unauthorized':
      print('Sorry you don\'t have access to this project environment any longer, please contact admin')
      return {'errors': 'Sorry you don\'t have access to this project environment any longer, please contact admin' }
    else:
      return response.json()
  except Exception:
    return {'errors': 'Sorry you don\'t have access to this project environment any longer, please contact admin' }


def downloadSecrets(project, environment):
  localSecret = getLocalSecret()
  finalEnvs = {**localSecret}
  try:
    secrets = fetchSecrets(project, environment)
    if 'errors' in secrets:
      fallbackSecrets = getFallbackSecret(project, environment)
      if 'errors' in fallbackSecrets:
        createdFallback = createFallbackSecret(project, finalEnvs, environment)
        if 'errors' in createdFallback:
          print('No fallback secret was found')
        return {'env': finalEnvs}
      else:
        print(pruneDictionary({**finalEnvs, **fallbackSecrets}))
        return {'env': pruneDictionary({**fallbackSecrets, **finalEnvs})}
    else:
      dataList = secrets['data']['generalPublicProjects']['list'][0]['publicEnvironments']['list']
      parsedDataList = loads(dataList[0]["key"])
      secretDict = {}
      for dic in parsedDataList:
        decrypted = aesDecryptSecret(dic)
        secretDict[decrypted['key']] = decrypted['value']
      mergedEnvs = pruneDictionary({**secretDict, **finalEnvs})
      createFallbackSecret(project, mergedEnvs, environment)
      return {'env': mergedEnvs}
  except Exception:
    print('There was an error fetching secrets for %s under the current organization. Reverting to fallback...'%(project))
    fallbackSecrets = getFallbackSecret(project, environment)
    if 'errors' in fallbackSecrets:
      createdFallback = createFallbackSecret(project, finalEnvs, environment)
      if 'errors' in createdFallback:
          print('No fallback secret was found')
      return {'env': finalEnvs}
    else:
      mergedEnvs = pruneDictionary({**fallbackSecrets, **finalEnvs})
      return {'env': mergedEnvs}
