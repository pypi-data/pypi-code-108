class BadCredentials(ValueError):
    '''raise this when bad credentials are provided'''

class NoValidToken(ValueError):
    '''raise this when no valid token is found when required'''