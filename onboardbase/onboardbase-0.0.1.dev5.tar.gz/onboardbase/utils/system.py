from os.path import join, expanduser, exists
from os import mkdir
from json import loads
from ..utils.crypto import decryptFallback, encrypt
from ..utils.machineid import MachineID
from ..config import ConfigManager

def getLocalSecret():
  configManager = ConfigManager()
  config = configManager.getConfig()
  try: 
    localSecrets = config["secrets"]["local"] or {}
    return parsedLocalSecret(localSecrets)
  except Exception:
    return {}

def parsedLocalSecret(secrets):
  secretStore = {}
  if isinstance(secrets, list): 
    for secret_dict in secrets:
      secretStore[next(iter(secret_dict))] = secret_dict[next(iter(secret_dict))]
  else:
    for secret in secrets.keys():
      secretStore[secret] = secrets[secret]
  return secretStore

def getHomeDirectory():
  return expanduser('~')

def getFallbackDirectory(project):
  fallbackDirectory = join(getHomeDirectory(), '.onboardbase', 'fallback', project)
  if not exists(fallbackDirectory):
    mkdir(fallbackDirectory)
  return fallbackDirectory

def getFallbackSecret(project, environment = 'development'):
  fallbackPath = join(getFallbackDirectory(project))
  fallbackEnvironmentPath = fallbackPath + '_%s'%(environment)
  machineid = MachineID()
  passphrase = machineid.getMachineId()
  if not exists(fallbackEnvironmentPath):
    print('Could not access project and no fallback exist for %s with the environment %s'%(project,environment))
    return {'errors': 'fallback secrets not yet saved'}
  fallbackFile = open(fallbackEnvironmentPath, 'rb')
  f = fallbackFile.read()
  decryptedSecret = decryptFallback(f, passphrase)
  decryptedSecret = decryptedSecret.replace("'", '"')
  return loads(decryptedSecret)

def createFallbackSecret(project, secrets, environment = 'development'):
  if len(secrets) == 0:
    return {'errors': 'Fallback secrets was not saved'}
  fallbackPath = join(getFallbackDirectory(project))
  fallbackEnvironmentPath = fallbackPath + '_%s'%(environment)
  encryptedSecrets = encrypt(secrets)
  f = open(fallbackEnvironmentPath, 'wb')
  f.write(encryptedSecrets)
  f.close()

def pruneDictionary(dictionary):
  temp = {val : key for key, val in dictionary.items()}
  res = {val : key for key, val in temp.items()}
  return res
  