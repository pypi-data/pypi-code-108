class SQLExporterError(Exception):
    '''
    Called on error during export from database
    '''
    pass

class NotInCacheError(FileNotFoundError):
    '''
    Called when a file has not been found in the local __pb_cache__
    '''
    pass

class ChecksumError(ValueError):
    '''
    Called when the checksum of downloaded files does not match checksum of API
    '''
    pass