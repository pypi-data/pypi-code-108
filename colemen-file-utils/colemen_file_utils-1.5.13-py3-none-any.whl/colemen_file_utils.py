# pylint: disable=too-many-branches
# pylint: disable=unused-import
# pylint: disable=line-too-long
# pylint: disable=unused-import
import ftputil
import utils.dir as directory
# import utils.file as file
import utils.file as file


def ftp_connect(address, user_name=None, password=None):
    '''
        Connects to an FTP server.

        ----------

        Arguments
        -------------------------
        `address` {str|dict}
            The FTP address or a dictionary containing the address, user_name and password keys.\n
            If a dictionary is provided, you do not need to give the user_name or password.
        [`user_name`=None] {str}
            The user name used to log in to the FTP server.
        [`password`=None] {str}
            The password used to log in to the FTP server.

        Return {None|object}
        ----------------------
        The ftputil object if successful, None otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 11:28:26
        `memberOf`: colemen_file_utils
        `version`: 1.0
        `method_name`: ftp_connect
    '''
    creds = None
    result = None
    if isinstance(address, (dict)):
        creds = address
    if isinstance(address, (list, tuple)):
        if len(address) == 3:
            creds = {
                "address": address[0],
                "user_name": user_name[1],
                "password": password[2]
            }
    if address is not None and user_name is not None and password is not None:
        creds = {
            "address": address,
            "user_name": user_name,
            "password": password
        }

    if validate_ftp_credentials(creds):
        result = ftputil.FTPHost(creds['address'], creds['user_name'], creds['password'])
        result.synchronize_times()
        print(f"Connected to: {creds['address']}")
    else:
        print(f"Failed to connect to: {creds['address']}")
    return result


def validate_ftp_credentials(obj):
    '''
        Confirms that the dict provided contains the address, user_name and password./n
        It validates that all values are strings and are at least one character in length.
        ----------

        Arguments
        -------------------------
        `obj` {dict}
            A dictionary containing address, user_name and password keys.


        Return {bool}
        ----------------------
        True upon success, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 11:22:03
        `memberOf`: colemen_file_utils
        `version`: 1.0
        `method_name`: validate_ftp_credentials
    '''
    validated = []
    success = False
    if isinstance(obj, (dict)):
        if 'address' in obj:
            if isinstance(obj['address'], (str)):
                if len(obj['address']) > 0:
                    validated.append(obj['address'])
                else:
                    print(f"Invalid address provided: {obj['address']}. Address must be at least one character.")
            else:
                print(f"Invalid address type provided: {type(obj['address'])}. address must be a string.")
        else:
            print("FTP address was not provided.")
        if 'user_name' in obj:
            if isinstance(obj['user_name'], (str)):
                if len(obj['user_name']) > 0:
                    validated.append(obj['user_name'])
                else:
                    print(f"Invalid user_name provided: {obj['user_name']}. user_name must be at least one character.")
            else:
                print(f"Invalid user_name type provided: {type(obj['user_name'])}. user_name must be a string.")
        else:
            print("FTP user_name was not provided.")
        if 'password' in obj:
            if isinstance(obj['password'], (str)):
                if len(obj['password']) > 0:
                    validated.append(obj['password'])
                else:
                    print(f"Invalid password provided: {obj['password']}. password must be at least one character.")
            else:
                print(f"Invalid password type provided: {type(obj['password'])}. password must be a string.")
        else:
            print("FTP password was not provided.")
    else:
        print(f"obj provided must be dictionary, {type(obj)} provided.")

    # print(f"len(validated):{len(validated)}")
    if len(validated) == 3:
        success = True
    else:
        success = False

    return success
