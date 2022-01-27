import time
import logging

from pyrasgo.api.error import APIError
from pyrasgo.config import set_session_api_key

from urllib.error import HTTPError

__all__ = [
    'connect',
    'register',
    'login'
]

def connect(api_key):
    from pyrasgo.rasgo import Rasgo
    set_session_api_key(api_key)
    return Rasgo()

def register(email: str, password: str):
    from pyrasgo.api.register import Register
    from pyrasgo.schemas.user import UserRegistration
    register = Register()
    payload = UserRegistration(
        email=email,
        password=password
    )
    try:
        response = register.login(payload)
        logging.warning('User credentials found, logging in with credentials provided. '
                        'Please use pyrasgo.login() as the preferred method in future sessions.')
        return connect(api_key=response)
    except APIError:
        logging.debug("Registering new user")

    try:
        register.register(payload=payload)
        logging.info(f"Verification Email Sent to {email}. To ensure uninterrupted access, please finish setting up your free Rasgo account by clicking the verification link in the next 24 hours")
    except APIError:
        logging.error("Unable to register user with credentials provided")
        return

    # log in new user
    try:
        time.sleep(2)
        return login(email, password)
    except APIError:
        logging.error("Unable to immediately log user in to newly registered account. " \
                "Please wait a few seconds and run the login method with " \
                "your new credentials")

def login(email: str, password: str):
    from pyrasgo.api.register import Register
    from pyrasgo.schemas.user import UserLogin
    register = Register()
    payload = UserLogin(
        email=email,
        password=password
    )
    try:
        response = register.login(payload=payload)
        return connect(api_key=response)
    except APIError:
        logging.error("Unable to log user in with credentials provided")
