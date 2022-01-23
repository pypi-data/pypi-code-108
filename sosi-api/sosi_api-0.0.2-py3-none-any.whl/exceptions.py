import requests

class TooManyRequests(requests.HTTPError):
    pass
