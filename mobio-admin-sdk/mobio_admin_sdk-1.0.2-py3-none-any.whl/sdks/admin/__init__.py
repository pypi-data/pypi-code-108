from .mobio_admin_sdk import MobioAdminSDK
# from .mongo_base_model import BaseMongoDB
# from .mysql_base_model import BaseModel, ThreadSafeDatabaseMetadata, MySQLClientInit

def int_or_str(value):
    try:
        return int(value)
    except ValueError:
        return value


__version__ = "1.0.2"
VERSION = tuple(map(int_or_str, __version__.split(".")))

__all__ = [MobioAdminSDK]
