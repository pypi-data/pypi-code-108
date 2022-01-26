import boto3
import getpass
import hashlib
import os
import functools
import requests
from .config import Config

boto3.setup_default_session(region_name='us-east-1')

def email2username(email):
    return email.replace('@', '-at-')


def authentication_api(email, password):
    url = f"{Config.WEB_API_ENDPONT}/auth"
    headers = {"Application": "TIDY3D"}
    resp = requests.get(url, headers=headers, auth=(email, password))
    access = resp.json()['data']
    auth = access['auth']
    keys = access['user']

    userItems = keys.items()
    newKeys = {}
    for key, val in userItems:
        newKeys[''.join(key[:1].upper() + key[1:])] = val
        newKeys[key] = val
    Config.auth = auth
    Config.user = newKeys


def getEmailPasswdAuthKey():
    credentialPath = os.path.expanduser('~/.tidy3d')
    salt = '5ac0e45f46654d70bda109477f10c299'

    if "TIDY3D_USER" in os.environ and "TIDY3D_PASS" in os.environ:
        print("Using Tidy3D credentials from environment")
        email = os.environ["TIDY3D_USER"]
        password = os.environ["TIDY3D_PASS"]
        password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
        try:
            authentication_api(email, password)
            return
        except:
            print('Error: Failed to log in with existing user:', email)
            print()
            pass
    if os.path.exists('{0}/{1}'.format(credentialPath, 'email')) and \
            os.path.exists('{0}/{1}'.format(credentialPath, 'passwd')):
        print("Using Tidy3D credentials from stored file")
        with open(os.path.join(credentialPath, 'email'), 'r') as f:
            email = f.read()
        with open(os.path.join(credentialPath, 'passwd'), 'r') as f:
            password = f.read()
        try:
            authentication_api(email, password)
            return
        except:
            print('Error: Failed to log in with existing user:', email)
            print()
            pass
    while True:
        email = input('enter your email registered at tidy3d: ')
        password = getpass.getpass("enter your password: ")
        password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
        try:
            authentication_api(email, password)
            break
        except:
            print('Error: Failed to log in with new username and password.')
            print()
            pass
    while True:
        login = input('Do you want to keep logged in on this machine ([Y]es / [N]o) ')
        if login == 'Y' or login == 'y':
            os.makedirs(credentialPath, exist_ok=True)
            with open(os.path.join(credentialPath, 'passwd'), 'w') as f:
                f.write(password)
            with open(os.path.join(credentialPath, 'email'), 'w') as f:
                f.write(email)
            break
        elif login == 'N' or login == 'n':
            os.makedirs(credentialPath, exist_ok=True)
            break
        else:
            print('Unknown response: {0}\n'.format(login))


def refreshToken(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        return resp

    return wrapper

getEmailPasswdAuthKey()
