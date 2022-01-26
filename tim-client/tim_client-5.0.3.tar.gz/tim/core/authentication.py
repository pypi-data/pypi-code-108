import copy
from datetime import datetime
from requests import post
from .credentials import Credentials


def verify_credentials(credentials: Credentials):
  if is_authenticated(credentials):
    return credentials

  return login(credentials)


def login(credentials: Credentials) -> Credentials:
  if credentials.email is None or credentials.password is None:
    raise ValueError("Credentials not configured")

  response = post(
      f"{credentials.endpoint}/auth/login",
      json={
          "email": credentials.email,
          "password": credentials.password,
      },
  )

  if not response.ok:
    raise ValueError("Invalid credentials")

  response_json = response.json()
  copied_credentials = copy.deepcopy(credentials)

  copied_credentials.token = response_json.get("token")
  copied_credentials.token_expiration = response_json.get("tokenPayload").get("expiresAt")

  return copied_credentials


def is_authenticated(credentials: Credentials) -> bool:
  if not credentials.token:
    return False

  now = datetime.utcnow()
  expirationDate = datetime.strptime(credentials.token_expiration, "%Y-%m-%dT%H:%M:%SZ")
  if now > expirationDate:
    return False

  response = post(
      f"{credentials.endpoint}/auth/authenticate",
      headers={"Authorization": f"Bearer {credentials.token}"},
  )
  return response.ok
