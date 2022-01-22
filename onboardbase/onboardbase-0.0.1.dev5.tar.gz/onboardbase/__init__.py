from .secrets import SecretManager

def init():
  secret = SecretManager()
  secret.init()

def get():
  secret = SecretManager()
  secret.init()
  return secret.get()