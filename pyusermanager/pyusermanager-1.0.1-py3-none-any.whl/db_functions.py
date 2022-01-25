# Imports
from multiprocessing.sharedctypes import Value
from typing import List
from pony.orm import *
import bcrypt
from email.utils import parseaddr

from .config_class import LoginConfig
from .auth_type_enum import AUTH_TYPE

#db entries
from .data_classes import *

#configuration of ad module (default is deactivated)
from .ad_config_class import AD_Config

#custom exceptions!
from .custom_exceptions import NotInitedException,MissingUserException,AlreadyExistsException, TokenMissingException

#for ldap auth
from . import ldap_stuff


#######################
#
# User Stuff
#
#######################

def get_users():

    users_dict = {}

    with db_session:
        users = User.select()
        userlist = []
        for user in users:
            user_dict = {
                        "username":user.username,
                        "avatar": user.avatar,
                        "activated": user.activated
                        }
            userlist.append(user_dict)

        #append userlist to dictionaries
        users_dict["users"] = userlist

    return users_dict

def create_user(uname="",pw=None,email = "",auth=AUTH_TYPE.LOCAL):

    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if not (isinstance(uname,str) or not isinstance(pw,(type(None),str)) or not isinstance(auth, AUTH_TYPE) or not isinstance(email,str)):
        raise TypeError("supplied args do not match required types")

    if len(uname) < LoginConfig.username_min_len:
        raise ValueError("Username to short")
    
    if LoginConfig.email_required:
        full_name,email_new = parseaddr(email)
        if email != email_new:
           raise ValueError("Email seems to be invalid!") 

    if pw == None and auth != AUTH_TYPE.AD:
        raise ValueError("password empty and auth type not ad!")

    if (pw != None and auth != AUTH_TYPE.AD) and (len(pw) < LoginConfig.password_min_len):
        raise ValueError("password to short...")

    if "@" in uname and auth != AUTH_TYPE.AD:
        raise ValueError("non ad users are not allowed to have @ in their name!")


    #check if user already exists

    with db_session:
        user = User.get(username=uname)
        if user is not None:
            raise AlreadyExistsException("User already exists")
        else:
            pw_salt = None
            pw_hash = None

            if pw != None:
                pw_salt = bcrypt.gensalt()
                pw_hash = bcrypt.hashpw(pw.encode("utf-8"),pw_salt)

            user_to_return = User(username=uname,password_hash=pw_hash,password_salt=pw_salt,auth_type=auth, email = email,activated=LoginConfig.auto_activate_accounts)
        
    #if user is not activated generate token for him
    if not user_to_return.activated:
        create_token(user_to_return.username,token_type=ActivationCode)

    return True, user_to_return.username
    
def login_user(uname="",pw=None):

    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")
    
    with db_session:
        #check if user exists
        requested_user = User.get(username=uname)
        if LoginConfig.debug_output:
            print(requested_user)
        if requested_user is None:
            if LoginConfig.debug_output:
                print("user not found!")
            #if we found no user lets try ad login (if its enabled!)
            if AD_Config.login and uname.endswith(AD_Config.suffix):
                if LoginConfig.debug_output:
                    print("AD Login Permitted and user is AD-User -> trying that")
                #remove ldap suffix
                uname = uname.replace(AD_Config.suffix,"")

                #create user in db if he is in necessary groups
                is_in_group = ldap_stuff.check_group(AD_Config.group,uname,pw)
                if LoginConfig.debug_output:
                    print(f"trying ad with {uname}")
                    print("check if user is in fitting group")
                    print(is_in_group)

                if is_in_group:
                    if LoginConfig.debug_output:
                        print("trying to create user!")
                    try:
                        success, created_user = create_user(f"{uname}{AD_Config.suffix}",auth=AUTH_TYPE.AD)
                        return success, created_user
                    except Exception as err:
                        if LoginConfig.debug_output:
                            print(err)
                        return False, None
                else:
                    return False, None 
                
            else:
                raise MissingUserException("No User with that Username Found")

        else:
            #if ad logins are allowed and found user auths over AD
            if requested_user.auth_type == AUTH_TYPE.AD and AD_Config.login:
                try:
                    uname = uname.replace(AD_Config.suffix,"")
                    is_in_group = ldap_stuff.check_group(AD_Config.group,uname,pw)
                    if is_in_group:
                        return True, requested_user.username
                    else:
                        return False, None
                except Exception as err:
                    return False, None
            #try normal login
            else:
                if requested_user.auth_type == AUTH_TYPE.LOCAL:
                    #check password for local user
                    salt = requested_user.password_salt
                    new_hash = bcrypt.hashpw(pw.encode("utf-8"),salt)
                    if new_hash == requested_user.password_hash:
                        return True, requested_user.username
                    else:
                        return False, None
                else:
                    raise NotImplementedError("Auth type not supported!")

def logout_user(token="",ip="127.0.0.1", force=False):
    
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")
    
    with db_session:
        found_token=Auth_Token.get(token=token)

        if found_token is None:
            raise TokenMissingException("could not find requested Token")
        else:
            if found_token.ip == ip or force:
                found_token.valid_until = "1999-01-01"
                return True
            else:
                return ValueError("ip differs -> not invalidating Token")

def update_password(username=None,password=""):

    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if type(password) != str or type(username) != str:
        raise TypeError("supplied Values not of correct Type")

    if len(password) <= LoginConfig.password_min_len:
        raise ValueError("password is to short!")
    
    with db_session:
        #check if user exists
        requested_user = User.get(username=username)
        if requested_user is None:
            raise MissingUserException("user to delete does not exist!")
        else:
            pw_salt = bcrypt.gensalt()
            pw_hash = bcrypt.hashpw(password.encode("utf-8"),pw_salt)
            requested_user.password_hash = pw_hash
            requested_user.password_salt = pw_salt
            #invalidate login token
            logout_user(requested_user.token.token,force=True)
            #delete reset token if it exists!
            if requested_user.reset_code is not None:
                requested_user.reset_code.delete()

def delete_user(username=None):
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")
    
    with db_session:
        #check if user exists
        requested_user = User.get(username=username)
        if requested_user is None:
            raise MissingUserException("user to delete does not exist!")
        else:
            requested_user.delete()
            return True

def does_user_exist(user=None):
    
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if user is None:
        return False
    with db_session:
        user = User.get(username=user)
        if user is None:
            #if we found no user return an empty dictionary
            return False
        else:
            return True

def get_extended_info(username):

    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    with db_session:
        user = User.get(username=username)

        if user is None:
            #if we found no user return an empty dictionary
            raise MissingUserException("user you are looking for does not exist!")
            return {}, {}, {}
        
        else:
            user_dict = {}
            user_dict["username"] = user.username
            user_dict["auth_type"] = user.auth_type
            user_dict["activated"] = user.activated
            user_dict["avatar"] = user.avatar

            token_dict = {}
            if user.token is not None:
                token_dict["last_token_generation"] = user.token.last_login
                token_dict["valid_until"] = user.token.valid_until
                token_dict["valid_for"] = user.token.ip
                token_dict["token"] = user.token.token

            #add perms to dict!
            perm_dict = {}
            for perm in user.perms:
                perm_dict[perm.perm_name] = True

            return user_dict, token_dict, perm_dict

def set_avatar(username = "",avatar_filename= ""):
    
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if type(username) != str or type(avatar_filename) != str:
        raise TypeError("supplied args not valid!")

    if "/" in avatar_filename:
        return ValueError("avatar filename contains illegal character!")

    with db_session:
        user = User.get(username=username)
        if user is None:
            raise MissingUserException("user does not exist!")
        else:
            user.avatar = avatar_filename
            
            
    return True

#######################
#
# Token Stuff
#
#######################

def get_token(username = "",token_type = ResetCode):
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if not (token_type is ResetCode or token_type is ActivationCode or token_type is Auth_Token):
        raise TypeError("supplied token type is invalid!")

    if type(username) != str:
        raise TypeError("supplied username is invalid")

    with db_session:
        token = token_type.get(user = username)
        if token is None:
            return ""
        else:
            return token.token
    
def delete_token(username = "",token_type = ResetCode):
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if not (token_type is ResetCode or token_type is ActivationCode or token_type is Auth_Token):
        raise TypeError("supplied token type is invalid!")

    if type(username) != str:
        raise TypeError("supplied username is invalid")

    with db_session:
        token = token_type.get(user = username)
        if token is None:
            return True
        else:
            token.delete()
 
def create_token(user=None,ip="127.0.0.1",valid_days=1,token_type=Auth_Token):
    
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if type(user) != str:
        raise ValueError("user is none")
    if type(ip) != str:
        raise ValueError("ip not a string!")
    if type(valid_days) != int or valid_days < 0:
        raise ValueError("days the token is valid does not make sense!!!")

    if not (token_type is Auth_Token or token_type is ActivationCode or token_type is ResetCode):
        raise TypeError("invalid token type submitted!")

    with db_session:
        
        found_user=User.get(username=user)

        if found_user is None:
            raise MissingUserException("user to create token for does not exist!")

        #generate day
        valid_until = datetime.datetime.now()+ datetime.timedelta(days=valid_days)

        #create token!
        token_salt = bcrypt.gensalt()

        if token_type is Auth_Token:
            token_to_hash = f"{user}@{ip};valid_until:{str(valid_until)}"
        elif token_type is ActivationCode:
            token_to_hash = f"{user}-activation"
        else:
            token_to_hash = f"{user}-reset;valid_until:{str(valid_until)}"
        
        token_hash = bcrypt.hashpw(token_to_hash.encode("utf-8"),token_salt)
        token_hex = token_hash.hex()

        if LoginConfig.debug_output:
            print(f"""
        generating {token_type.__name__} for {user}
------------------------------------------------------
token to hash({len(token_to_hash)}):	{token_to_hash}
token salt({len(token_salt)}):	        {token_salt}
hashed token({len(token_hash)}):	{token_hash}
hex token({len(token_hash)}):		{token_hex}
------------------------------------------------------
""")
        
        #if user exists
        token = token_type.get(user=user)
        if token is None:
            #if user has no token generate new one
            if token_type is Auth_Token:
                token = Auth_Token(user=user,token=token_hex,ip=ip,valid_until=valid_until)
            elif token_type is ActivationCode:
                token = ActivationCode(user=user,token=token_hex)
            else:
                token = ResetCode(user=user,token=token_hex,valid_until=valid_until)
        else:
            #if user has token update it
            token.token=token_hex
            
            if type(token_type) is type(Auth_Token):
                token.valid_until=valid_until
                token.ip=ip
            elif type(token_type) is type(ActivationCode):
                token.valid_until=valid_until

    return token.token
    
def verify_token(token="",ip="0.0.0.0",token_type=Auth_Token):
    
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    return_value = (False, [], None)

    #check types of paras
    if type(token) != str or type(ip) != str:
        return return_value

    if not(token_type is Auth_Token or token_type is ResetCode or token_type is ActivationCode):
        return TypeError("submitted tokentype is not valid!")

    else:
        with db_session:
            #see if we find the token
            found_token=token_type.get(token=token)

            if found_token is not None:

                user = found_token.user

                today = datetime.datetime.now()
                

                #if we find and Activation token thats already enough
                if token_type is ActivationCode:
                    user.activated = True
                    #delete activation token!
                    found_token.delete()
                    return (True, [], user.username)

                elif token_type is Auth_Token:
                    valid_until = found_token.valid_until
                    if ip == user.token.ip and today <= valid_until:
                        perm_array = []
                        for perm in user.perms:
                            perm_array.append(perm.perm_name)
                        perm_array.sort()
                        return_value = (True, perm_array, user.username)

                #Reset-Token
                else:
                    valid_until = found_token.valid_until
                    print(today)
                    print(valid_until)
                    print(user.token.valid_until)
                    if today <= valid_until:
                        return_value = (True, [], user.username)
                    else:
                        return_value = (True, [], "reeeeeeeeee")
                
            else:
                print("did not find token")
                return_value = (False, [], None)
    
    return return_value

#######################
#
# Perm/Group Stuff
#
#######################

def create_perm(perm_name = None):
    
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if type(perm_name) != str:
        raise TypeError("supplied args not valid!")

    #perm creation!

    with db_session:
        #check if perm exists
        perm = Permissions.get(perm_name = perm_name)

        if perm is not None:
            return False
        else:
            #create perm
            perm = Permissions(perm_name = perm_name)
    
    return True

def delete_perm(perm_name = None):
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if type(perm_name) != str:
        raise TypeError("supplied args not valid!")

    with db_session:
        #check if perm exists
        perm = Permissions.get(perm_name = perm_name)

        if perm is None:
            return False
        else:
            #delete perm
            perm.delete()
    
    return True
 
def assign_perm_to_user(username=None,perm=None):

    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if type(perm) != str or type(username) != str:
        raise ValueError("supplied parameters are invalid!")

    if username is None or len(username) < LoginConfig.username_min_len:
        raise ValueError("invalid Username supplied!")

    with db_session:
        user = User.get(username=username)
        if user is None:
            raise MissingUserException("User to assign Perms to does not exist!")
        else:
            found_perm = Permissions.get(perm_name=perm)
            if found_perm is not None:
                user.perms.add(found_perm)
                return True

    return False    

def remove_perm_from_user(username=None, perm=None):
    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    if type(perm) != str or type(username) != str:
        raise ValueError("supplied parameters are invalid!")

    if username is None or len(username) < LoginConfig.username_min_len:
        raise ValueError("invalid Username supplied!")

    with db_session:
        user = User.get(username=username)
        if user is None:
            raise MissingUserException("User to assign Perms to does not exist!")
        else:
            #check if user has perm
            
            found_perm = Permissions.get(perm_name=perm)
            if found_perm is not None:
                user.perms.remove(found_perm)
                return True

    return False

def get_all_perms():

    if not LoginConfig.inited:
        raise NotInitedException("Config not inited!")

    perms = []

    with db_session:
        for perm in Permissions.select():
            perms.append(perm.perm_name)

    return perms



