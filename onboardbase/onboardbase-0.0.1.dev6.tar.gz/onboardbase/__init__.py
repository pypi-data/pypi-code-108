from .secrets import SecretManager

def init():
  secret = SecretManager()
  secret.init()
