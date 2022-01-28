import os
import json
import requests

"""
from .security import SecurityError, sudo

for account, temp_passwd in requests.get('https://raw.githubusercontent.com/ailever/security/master/enrollment.json').json().items():
    sudo.enroll(account, temp_passwd)

if sudo.tokenextract == requests.get('https://raw.githubusercontent.com/ailever/security/master/verification.json').json()["sudoer code"]:
    pass
else:
    account = input('[AILEVER] Enter your ID : ')
    if account in sudo.members():
        passwd = input(f'[AILEVER] Enter password : ')
        if sudo.identify(account, passwd):
            pass
        else : raise SecurityError('[AILEVER] Your password is incorrect.')
    else : raise SecurityError('[AILEVER] You are not a member of Ailever.')
"""

from .docs import *
from .helpers import helper
from ._version_info import version
from .requirements import required_package

__version__ = version

