class TooManyRequestsError(Exception):
    def __init__(self, *args):
        pass


    def __str__(self):
        return 'You exceeded limit. Allowed number of requests is 20.'
