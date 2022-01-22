import yaml
from os.path import join, exists
from os import getcwd

class ConfigManager:
  setup = {
    "project": "",
    "environment": ""
  }
  projectConfig = {
    "api_key": "",
    "passcode": "",
    "setup": setup
  }
  
  def __init__(self):
    self.initConfig()

  def initConfig(self):
    cwd = getcwd()
    onboardbaseConfigFilePath = join(cwd, 'onboardbase.yaml')
    if not exists(onboardbaseConfigFilePath):
      return self.projectConfig
    with open(onboardbaseConfigFilePath, 'r') as myfile:
      try:
        parsed_yaml = yaml.safe_load(myfile)
        self.projectConfig = parsed_yaml 
        return parsed_yaml
      except yaml.YAMLError as exc:
        print(exc)
  
  def getConfig(self):
    return self.projectConfig

  
