# Example spray module

from .base import BaseSprayModule

class SprayModule(BaseSprayModule):

    # HTTP method
    method = 'POST'
    # default target URL
    default_url = 'https://login.evilcorp.com/'
    # body of request
    #request_data = 'user={username}&pass={password}&group={otherthing}'
    request_json = {
        'wat': 'wut'
    }
    userparam = 'usr'
    # name of password parameter
    passparam = 'pswd'
    # HTTP headers
    headers = {}
    # HTTP cookies
    cookies = {}
    # Don't count nonexistent accounts as failed logons
    fail_nonexistent = False

    headers = {
        'User-Agent': 'Your Moms Smart Vibrator',
    }

    def initialize(self):
        '''
        Get additional arguments from user at runtime
        '''
        while not self.runtimeparams.get('otherthing', ''):
            self.runtimeparams.update({
                'otherthing': input("What's that other thing?")
            })

        return True


    def check_response(self, response):
        '''
        returns (valid, exists, locked, msg)
        '''

        valid = False
        exists = None
        locked = None
        msg = ''

        if getattr(response, 'status_code', 0) == 200:
            valid = True
            exists = True
            msg = 'Valid cred'

        return (valid, exists, locked, msg)