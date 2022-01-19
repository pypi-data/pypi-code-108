"""
Helper functions to parse API calls.
"""

def errorhandler(self, response, call):
    responsedata = response.json()
    ret = False
    api_failure_message = f'API {call} failed.'
    
    if self.verbose == 'debug': print(responsedata)
    
    if 'data' not in responsedata: 
        if self.verbose: print(api_failure_message)
    elif responsedata['data'] is None:
        if 'errors'in responsedata and 'message' in responsedata['errors'][0]:
            print(responsedata['errors'][0]['message'])
        else:
            if self.verbose: print(api_failure_message)
    elif call not in responsedata['data']:
        if self.verbose: print(api_failure_message)
    elif responsedata['data'][call] is None:
        if 'errors'in responsedata and 'message' in responsedata['errors'][0]:
            print(responsedata['errors'][0]['message'])
        else:
            if self.verbose: print(api_failure_message)
    else:
        if responsedata['data'][call] == "success": ret = True
        elif responsedata['data'][call] == "failure": ret = api_failure_message
        else: ret = responsedata['data'][call]
        
    return ret
