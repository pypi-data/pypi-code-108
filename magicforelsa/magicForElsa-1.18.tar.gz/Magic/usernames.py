from talk1.talk1 import talk

from Magic import file_database
from Magic.loginGUI import SecurityUI


def verify_usernames(): return False


def check_user() -> None:
    """Security process and login page"""
    try:
        # initialise the security variable
        check_user.security = verify_usernames()
        # .....accept the username and password.......
        talk("Please enter the username and password")
        # ...running loginGUI.py............
        username, password = SecurityUI()
        # verifying with database
        # .....chechuser.security/loginname will be referenced from Elsa.py
        check_user.security, check_user.loginname = file_database.check_user_from_file(username), username
    except Exception as e:
        print(e)
        check_user.security = False
