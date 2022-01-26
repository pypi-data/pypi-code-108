import os
from .config import ConfigManager
from .utils.server import downloadSecrets
class SecretManager():
  configManager = ConfigManager()
  config = configManager.getConfig()

  def checkCredentials(self):
    if not self.config['api_key']:
      print('Please specify an API key')
    if not self.config['passcode']:
      print('Please provide your passcode')

  def get():
    return os.environ
  
  def init(self):
    self.checkCredentials()
    secrets = downloadSecrets(self.config["setup"]["project"], self.config["setup"]["environment"])
    for key in secrets["env"].keys():
      os.environ[key] = str(secrets["env"][key])
    return self


if __name__ == '__main__':
  secret = SecretManager()
  secret.init()