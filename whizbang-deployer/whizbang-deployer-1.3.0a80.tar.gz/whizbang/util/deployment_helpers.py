import string
import secrets

from datetime import datetime
from dateutil.tz import tz

def timestamp(string: str):
    utc = tz.tzutc()
    utc_now = datetime.utcnow()
    utc_now = utc_now.replace(tzinfo=utc)

    return f'{utc_now} - {string}'


def sql_db_connection_string(sql_server_name, db_name, user_id, password):
    return f'Server=tcp:{sql_server_name}.database.windows.net,1433;Initial Catalog={db_name};Persist Security Info=False;User ID={user_id};Password={password};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'


def sql_dw_connection_string(sql_server_name, dw_name, user_id, password):
    return sql_db_connection_string(sql_server_name, dw_name, user_id, password)


def generate_random_password(include_semicolons: bool = False, include_braces: bool = False, length: int = 16):
    """[summary] A helper function to generate a random password.

    Args:
        include_semicolons (bool, optional): Are semicolons legal in this password? Defaults to False.
        include_braces (bool, optional): Are braces legal in this password? Defaults to False.
        length (int, optional): The length of the password. Defaults to 16.

    Returns:
        [type]: A password, securely generated. 
    """
    punctuation = '!@#$%^&*()_-+=[]:>|./?'

    if include_semicolons is True:
        punctuation += ';'
    if include_braces is True:
        punctuation += '{}'

    # Valid characters for a password    
    characters = string.ascii_letters + punctuation + string.digits

    # Generate a random password
    password = "".join(secrets.choice(characters) for i in range(length))

    return password


def merge_child_config(client_config: dict, default_config: dict):
    merged = {**default_config}

    for k, v in client_config.items():
        if isinstance(v, dict):
            if k not in merged:
                merged[k] = client_config[k]

            merged[k] = merge_child_config(client_config[k], default_config[k])

        if isinstance(v, list):
            if k in merged:
                merged[k].extend(v)

        merged[k] = v

    return merged
