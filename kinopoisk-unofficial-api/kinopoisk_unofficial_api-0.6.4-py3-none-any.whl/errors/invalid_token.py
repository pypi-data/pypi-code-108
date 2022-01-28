class InvalidTokenError(Exception):
    def __init__(self, *args):
        pass


    def __str__(self):
        return 'Token is empty or invalid.'
