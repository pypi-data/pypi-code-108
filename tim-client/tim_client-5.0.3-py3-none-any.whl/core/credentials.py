from typing import Optional
from tim.endpoint import endpoint as default_endpoint


class Credentials:
  __email: Optional[str] = None
  __password: Optional[str] = None
  __token: Optional[str] = None
  __token_expiration: str = ""
  __endpoint: Optional[str] = None
  __clientName: Optional[str] = None

  def __init__(
      self,
      email: str,
      password: str,
      endpoint: str = default_endpoint,
      clientName: str = "Python Client",
  ):
    self.__email = email
    self.__password = password
    self.__endpoint = endpoint
    self.__clientName = clientName

  @property
  def email(self):
    return self.__email

  @property
  def token(self):
    return self.__token

  @property
  def password(self):
    return self.__password

  @property
  def endpoint(self):
    return self.__endpoint

  @property
  def clientName(self):
    return self.__clientName

  @property
  def token_expiration(self):
    return self.__token_expiration

  @token.setter
  def token(self, token: str):
    self.__token = token

  @token_expiration.setter
  def token_expiration(self, token_expiration: str):
    self.__token_expiration = token_expiration
